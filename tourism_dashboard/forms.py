import io

import pandas as pd
from django import forms
from django.conf import settings

from .charts import CHART_TYPES, CSV_COLUMNS, X_AXES, Y_AXES

REQUIRED_COLUMNS = list(CSV_COLUMNS)


def read_tourism_csv(fileobj):
    """Parse and validate a tourism CSV. Returns a DataFrame with model field names.

    Raises ``forms.ValidationError`` with a user-friendly message on bad input.
    """
    try:
        df = pd.read_csv(fileobj)
    except Exception as exc:  # pandas raises many different parser errors
        raise forms.ValidationError(f'Could not read the file as CSV ({exc.__class__.__name__}).')

    df.columns = [str(c).strip() for c in df.columns]
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise forms.ValidationError('Missing column(s): ' + ', '.join(missing))
    if df.empty:
        raise forms.ValidationError('The file has a header but no data rows.')

    df = df[REQUIRED_COLUMNS].rename(columns=CSV_COLUMNS)
    for col in ('year', 'visitor_count'):
        numbers = pd.to_numeric(df[col], errors='coerce')
        bad = numbers.isna() | (numbers < 0) | (numbers % 1 != 0)
        if bad.any():
            first = int(bad.idxmax()) + 2  # +1 header, +1 one-based
            raise forms.ValidationError(f'Row {first}: "{col}" must be a whole, non-negative number.')
        df[col] = numbers.astype(int)
    for col in ('country', 'region', 'visitor_type', 'season', 'age_group'):
        df[col] = df[col].fillna('').astype(str).str.strip().str.slice(0, 100)
        if (df[col] == '').any():
            first = int((df[col] == '').idxmax()) + 2
            raise forms.ValidationError(f'Row {first}: "{col}" is empty.')
    return df


class TourismDataUploadForm(forms.Form):
    data_file = forms.FileField(
        label='CSV file',
        help_text='Columns: ' + ', '.join(REQUIRED_COLUMNS),
        widget=forms.ClearableFileInput(attrs={'accept': '.csv,text/csv'}),
    )
    replace_existing = forms.BooleanField(
        required=False,
        label='Replace my existing data instead of adding to it',
    )

    def clean_data_file(self):
        upload = self.cleaned_data['data_file']
        if not upload.name.lower().endswith('.csv'):
            raise forms.ValidationError('Please upload a .csv file.')
        if upload.size > settings.MAX_UPLOAD_BYTES:
            limit_mb = settings.MAX_UPLOAD_BYTES / (1024 * 1024)
            raise forms.ValidationError(f'File is too large (limit {limit_mb:.0f} MB).')
        self.dataframe = read_tourism_csv(io.BytesIO(upload.read()))
        return upload


class CustomVisualizationForm(forms.Form):
    title = forms.CharField(max_length=200)
    chart_type = forms.ChoiceField(choices=CHART_TYPES)
    years = forms.MultipleChoiceField(required=False, help_text='Leave empty for all years.')
    regions = forms.MultipleChoiceField(required=False, help_text='Leave empty for all regions.')
    x_axis = forms.ChoiceField(choices=X_AXES, label='X axis')
    y_axis = forms.ChoiceField(choices=Y_AXES, label='Values')

    def __init__(self, *args, years=(), regions=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['years'].choices = [(str(y), str(y)) for y in years]
        self.fields['regions'].choices = [(r, r) for r in regions]

    def to_model_kwargs(self):
        data = self.cleaned_data
        return {
            'title': data['title'],
            'chart_type': data['chart_type'],
            'data_filters': {'years': data['years'], 'regions': data['regions']},
            'chart_config': {'x_axis': data['x_axis'], 'y_axis': data['y_axis']},
        }

from django import forms
from .models import TourismData, CustomVisualization

class TourismDataUploadForm(forms.ModelForm):
    data_file = forms.FileField(
        label='Select CSV File',
        help_text='File must contain columns: Year, Country, Region, Visitor_Count, Visitor_Type, Season, Age_Group'
    )

    class Meta:
        model = TourismData
        fields = ['data_file']

class CustomVisualizationForm(forms.ModelForm):
    class Meta:
        model = CustomVisualization
        fields = ['title', 'chart_type', 'data_filters', 'chart_config']
        widgets = {
            'data_filters': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'chart_config': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_filters'].widget.attrs.update({'class': 'form-control'})
        self.fields['chart_config'].widget.attrs.update({'class': 'form-control'}) 
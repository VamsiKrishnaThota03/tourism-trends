import csv
import json
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from . import charts
from .forms import CustomVisualizationForm, TourismDataUploadForm, read_tourism_csv
from .models import CustomVisualization, TourismData, UserDashboard

SAMPLE_CSV = Path(settings.BASE_DIR) / 'data' / 'tourism_data.csv'
EXPORT_HEADER = list(charts.CSV_COLUMNS)


def _user_data(request):
    return TourismData.objects.filter(uploaded_by=request.user)


def _filter_options(queryset):
    # .order_by() clears Meta.ordering, which would otherwise break .distinct().
    queryset = queryset.order_by()
    return {
        'years': sorted(queryset.values_list('year', flat=True).distinct()),
        'regions': sorted(queryset.values_list('region', flat=True).distinct()),
        'visitor_types': sorted(queryset.values_list('visitor_type', flat=True).distinct()),
    }


def _save_rows(user, df, replace=False):
    with transaction.atomic():
        if replace:
            TourismData.objects.filter(uploaded_by=user).delete()
        TourismData.objects.bulk_create(
            [TourismData(uploaded_by=user, **row) for row in df.to_dict('records')],
            batch_size=1000,
        )
    return len(df)


@login_required
def dashboard(request):
    user_dashboard, _ = UserDashboard.objects.get_or_create(user=request.user)
    data = _user_data(request)
    totals = data.aggregate(visitors=Sum('visitor_count'))
    options = _filter_options(data)
    default_view = user_dashboard.default_view
    if default_view not in charts.BUILTIN_VIEWS:
        default_view = 'yearly_trends'
    context = {
        'default_view': default_view,
        'custom_filters': user_dashboard.custom_filters or {},
        'custom_visualizations': CustomVisualization.objects.filter(user=request.user),
        'record_count': data.count(),
        'total_visitors': totals['visitors'] or 0,
        'country_count': data.order_by().values('country').distinct().count(),
        **options,
    }
    return render(request, 'tourism_dashboard/dashboard.html', context)


@login_required
def upload_data(request):
    if request.method == 'POST':
        form = TourismDataUploadForm(request.POST, request.FILES)
        if form.is_valid():
            count = _save_rows(request.user, form.dataframe, form.cleaned_data['replace_existing'])
            messages.success(request, f'Upload complete: {count} records imported.')
            return redirect('dashboard')
    else:
        form = TourismDataUploadForm()
    return render(request, 'tourism_dashboard/upload.html', {'form': form})


@login_required
@require_POST
def load_sample_data(request):
    with SAMPLE_CSV.open('rb') as fh:
        df = read_tourism_csv(fh)
    count = _save_rows(request.user, df, replace=True)
    messages.success(request, f'Sample dataset loaded ({count} records).')
    return redirect('dashboard')


@login_required
def create_visualization(request):
    options = _filter_options(_user_data(request))
    form = CustomVisualizationForm(request.POST or None, years=options['years'],
                                   regions=options['regions'])
    if request.method == 'POST' and form.is_valid():
        CustomVisualization.objects.create(user=request.user, **form.to_model_kwargs())
        messages.success(request, 'Visualization saved to your dashboard.')
        return redirect('dashboard')
    return render(request, 'tourism_dashboard/create_visualization.html',
                  {'form': form, 'has_data': bool(options['years'])})


@login_required
@require_POST
def update_dashboard_preferences(request):
    try:
        payload = json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({'status': 'error', 'message': 'Expected an object'}, status=400)

    user_dashboard, _ = UserDashboard.objects.get_or_create(user=request.user)
    view = payload.get('default_view')
    if view is not None:
        if view not in charts.BUILTIN_VIEWS:
            return JsonResponse({'status': 'error', 'message': 'Unknown view'}, status=400)
        user_dashboard.default_view = view
    filters = payload.get('custom_filters')
    if filters is not None:
        if not isinstance(filters, dict):
            return JsonResponse({'status': 'error', 'message': 'custom_filters must be an object'},
                                status=400)
        allowed = ('year_range', 'region', 'visitor_type')
        user_dashboard.custom_filters = {k: str(filters.get(k, ''))[:100] for k in allowed}
    user_dashboard.save()
    return JsonResponse({'status': 'success'})


@login_required
@require_POST
def delete_visualization(request, viz_id):
    visualization = get_object_or_404(CustomVisualization, id=viz_id, user=request.user)
    visualization.delete()
    messages.success(request, f'Deleted "{visualization.title}".')
    return redirect('dashboard')


@login_required
@require_GET
def get_visualization_data(request, view_type):
    if view_type not in charts.BUILTIN_VIEWS:
        return JsonResponse({'error': 'Unknown view type'}, status=404)
    queryset = charts.apply_filters(
        _user_data(request),
        year_range=request.GET.get('year_range'),
        region=request.GET.get('region'),
        visitor_type=request.GET.get('visitor_type'),
    )
    return JsonResponse({view_type: charts.builtin_figure(view_type, queryset)})


@login_required
@require_GET
def chart_preview(request):
    """Figure for an unsaved custom visualization (used by the create form preview)."""
    queryset = charts.apply_filters(_user_data(request), years=request.GET.getlist('years'),
                                    regions=request.GET.getlist('regions'))
    try:
        figure = charts.custom_figure(queryset, request.GET.get('chart_type'),
                                      request.GET.get('x_axis'), request.GET.get('y_axis'),
                                      request.GET.get('title', ''))
    except ValueError as exc:
        return JsonResponse({'error': str(exc)}, status=400)
    return JsonResponse(figure)


@login_required
@require_GET
def custom_visualization_data(request, viz_id):
    viz = get_object_or_404(CustomVisualization, id=viz_id, user=request.user)
    filters = viz.data_filters if isinstance(viz.data_filters, dict) else {}
    config = viz.chart_config if isinstance(viz.chart_config, dict) else {}
    queryset = charts.apply_filters(_user_data(request), years=filters.get('years'),
                                    regions=filters.get('regions'))
    try:
        figure = charts.custom_figure(queryset, viz.chart_type, config.get('x_axis', 'year'),
                                      config.get('y_axis', 'visitor_count'), viz.title)
    except ValueError as exc:
        return JsonResponse({'error': str(exc)}, status=400)
    return JsonResponse(figure)


@login_required
@require_GET
def debug_data(request):
    """Quick check of what is stored for the current user."""
    data = _user_data(request)
    sample = data.values(*charts.CSV_COLUMNS.values())[:5]
    return JsonResponse({'count': data.count(), 'sample': list(sample)})


@login_required
def export_data_for_tableau(request):
    """Download the current user's data as CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tourism_data_for_tableau.csv"'
    writer = csv.writer(response)
    writer.writerow(EXPORT_HEADER)
    for row in _user_data(request).values_list(*charts.CSV_COLUMNS.values()):
        writer.writerow(row)
    return response


@login_required
def tableau_dashboard(request):
    return render(request, 'tourism_dashboard/tableau_dashboard.html',
                  {'record_count': _user_data(request).count()})


@login_required
@require_GET
def tableau_wdc(request):
    """Tableau Web Data Connector page. Open it from Tableau's 'Web Data Connector'
    option; you will be asked to log in first, then the connector reads your data."""
    return render(request, 'tourism_dashboard/tableau_wdc.html')


@login_required
@require_GET
def tableau_wdc_data(request):
    rows = [dict(zip(EXPORT_HEADER, values))
            for values in _user_data(request).values_list(*charts.CSV_COLUMNS.values())]
    return JsonResponse({'data': rows})

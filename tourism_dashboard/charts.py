"""Aggregations that turn TourismData rows into Plotly.js figure dicts."""
from django.db.models import Sum

CSV_COLUMNS = {
    'Year': 'year',
    'Country': 'country',
    'Region': 'region',
    'Visitor_Count': 'visitor_count',
    'Visitor_Type': 'visitor_type',
    'Season': 'season',
    'Age_Group': 'age_group',
}

CHART_TYPES = [
    ('line', 'Line chart'),
    ('bar', 'Bar chart'),
    ('pie', 'Pie chart'),
    ('scatter', 'Scatter plot'),
    ('heatmap', 'Heatmap'),
]
X_AXES = [
    ('year', 'Year'),
    ('country', 'Country'),
    ('region', 'Region'),
    ('season', 'Season'),
]
Y_AXES = [
    ('visitor_count', 'Total visitors'),
    ('visitor_type', 'Visitors split by visitor type'),
    ('age_group', 'Visitors split by age group'),
]
LABELS = dict(X_AXES + [('visitor_type', 'Visitor type'), ('age_group', 'Age group'),
                        ('visitor_count', 'Visitors')])

BUILTIN_VIEWS = ('yearly_trends', 'regional_distribution', 'demographics')

PALETTE = ['#2563eb', '#0d9488', '#f59e0b', '#db2777', '#7c3aed', '#16a34a', '#ea580c', '#0891b2']


def _layout(title, **extra):
    layout = {
        'title': {'text': title, 'font': {'size': 16}},
        'margin': {'t': 64, 'r': 16, 'b': 48, 'l': 64},
        'font': {'family': 'Inter, system-ui, sans-serif', 'color': '#334155'},
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'colorway': PALETTE,
        'xaxis': {'gridcolor': '#e2e8f0'},
        'yaxis': {'gridcolor': '#e2e8f0', 'rangemode': 'tozero'},
        'legend': {'orientation': 'h', 'x': 1, 'xanchor': 'right', 'y': 1.02, 'yanchor': 'bottom'},
    }
    layout.update(extra)
    return layout


def parse_year_range(value):
    """Accept '2021' or '2020-2023'. Returns (start, end) or None if invalid/empty."""
    value = (value or '').strip()
    if not value:
        return None
    parts = value.split('-')
    try:
        if len(parts) == 1:
            year = int(parts[0])
            return year, year
        if len(parts) == 2:
            start, end = int(parts[0]), int(parts[1])
            return (start, end) if start <= end else (end, start)
    except ValueError:
        pass
    return None


def apply_filters(queryset, year_range=None, region=None, visitor_type=None,
                  years=None, regions=None):
    span = parse_year_range(year_range)
    if span:
        queryset = queryset.filter(year__gte=span[0], year__lte=span[1])
    if region:
        queryset = queryset.filter(region=region)
    if visitor_type:
        queryset = queryset.filter(visitor_type=visitor_type)
    if years:
        queryset = queryset.filter(year__in=[int(y) for y in years if str(y).isdigit()])
    if regions:
        queryset = queryset.filter(region__in=regions)
    return queryset


def builtin_figure(view_type, queryset):
    if view_type == 'yearly_trends':
        rows = queryset.values('year').annotate(total=Sum('visitor_count')).order_by('year')
        return {
            'data': [{
                'x': [r['year'] for r in rows],
                'y': [r['total'] for r in rows],
                'type': 'scatter', 'mode': 'lines+markers', 'name': 'Total visitors',
                'line': {'width': 3}, 'marker': {'size': 8},
            }],
            'layout': _layout('Yearly tourism trends',
                              xaxis={'title': {'text': 'Year'}, 'dtick': 1, 'gridcolor': '#e2e8f0'},
                              yaxis={'title': {'text': 'Visitors'}, 'gridcolor': '#e2e8f0',
                                     'rangemode': 'tozero'}),
        }
    if view_type == 'regional_distribution':
        rows = queryset.values('region').annotate(total=Sum('visitor_count')).order_by('-total')
        return {
            'data': [{
                'labels': [r['region'] for r in rows],
                'values': [r['total'] for r in rows],
                'type': 'pie', 'hole': 0.45, 'name': 'Regions', 'sort': False,
                'marker': {'colors': PALETTE},
            }],
            'layout': _layout('Visitors by region'),
        }
    if view_type == 'demographics':
        rows = queryset.values('visitor_type').annotate(total=Sum('visitor_count')).order_by('-total')
        return {
            'data': [{
                'x': [r['visitor_type'] for r in rows],
                'y': [r['total'] for r in rows],
                'type': 'bar', 'name': 'Visitor types',
                'marker': {'color': PALETTE[:max(len(rows), 1)]},
            }],
            'layout': _layout('Visitors by type',
                              xaxis={'title': {'text': 'Visitor type'}},
                              yaxis={'title': {'text': 'Visitors'}, 'gridcolor': '#e2e8f0'}),
        }
    raise ValueError(f'Unknown view type: {view_type}')


def custom_figure(queryset, chart_type, x_axis, y_axis, title=''):
    """Build a figure for a saved custom visualization.

    The value plotted is always the summed visitor count. When ``y_axis`` is a
    category (visitor type / age group) the data is split into one series per
    category; for heatmaps it becomes the second axis.
    """
    valid_x = dict(X_AXES)
    valid_y = dict(Y_AXES)
    if chart_type not in dict(CHART_TYPES) or x_axis not in valid_x or y_axis not in valid_y:
        raise ValueError('Invalid chart configuration')

    title = title or f'Visitors by {LABELS[x_axis].lower()}'
    split = None if y_axis == 'visitor_count' else y_axis

    if chart_type == 'pie':
        rows = queryset.values(x_axis).annotate(total=Sum('visitor_count')).order_by('-total')
        return {
            'data': [{'labels': [str(r[x_axis]) for r in rows], 'values': [r['total'] for r in rows],
                      'type': 'pie', 'hole': 0.45, 'sort': False, 'marker': {'colors': PALETTE}}],
            'layout': _layout(title),
        }

    if chart_type == 'heatmap':
        second = split or 'visitor_type'
        rows = queryset.values(x_axis, second).annotate(total=Sum('visitor_count'))
        xs = sorted({r[x_axis] for r in rows})
        ys = sorted({r[second] for r in rows})
        grid = {(r[x_axis], r[second]): r['total'] for r in rows}
        return {
            'data': [{
                'x': [str(x) for x in xs], 'y': [str(y) for y in ys],
                'z': [[grid.get((x, y), 0) for x in xs] for y in ys],
                'type': 'heatmap', 'colorscale': [[0, '#eff6ff'], [1, '#1d4ed8']],
            }],
            'layout': _layout(title, xaxis={'title': {'text': LABELS[x_axis]}, 'type': 'category'},
                              yaxis={'title': {'text': LABELS[second]}, 'type': 'category'}),
        }

    trace_type = 'bar' if chart_type == 'bar' else 'scatter'
    mode = 'lines+markers' if chart_type == 'line' else 'markers'

    def trace(name, rows):
        item = {'x': [str(r[x_axis]) for r in rows], 'y': [r['total'] for r in rows],
                'type': trace_type, 'name': name}
        if trace_type == 'scatter':
            item['mode'] = mode
            item['marker'] = {'size': 9}
        return item

    if split:
        rows = list(queryset.values(x_axis, split).annotate(total=Sum('visitor_count')).order_by(x_axis))
        groups = sorted({r[split] for r in rows})
        data = [trace(str(g), [r for r in rows if r[split] == g]) for g in groups]
    else:
        rows = queryset.values(x_axis).annotate(total=Sum('visitor_count')).order_by(x_axis)
        data = [trace('Visitors', rows)]

    return {
        'data': data,
        'layout': _layout(title, barmode='group',
                          xaxis={'title': {'text': LABELS[x_axis]}, 'type': 'category',
                                 'gridcolor': '#e2e8f0'},
                          yaxis={'title': {'text': 'Visitors'}, 'gridcolor': '#e2e8f0',
                                 'rangemode': 'tozero'}),
    }

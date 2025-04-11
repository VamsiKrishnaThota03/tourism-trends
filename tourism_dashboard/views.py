from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from .models import TourismData, UserDashboard, CustomVisualization
from .forms import TourismDataUploadForm, CustomVisualizationForm
import pandas as pd
import json
from django.db.models import Sum, Count
import plotly.graph_objects as go
import csv
import io
from django.views.decorators.csrf import csrf_exempt

@login_required
def dashboard(request):
    user_dashboard, created = UserDashboard.objects.get_or_create(user=request.user)
    custom_visualizations = CustomVisualization.objects.filter(user=request.user)
    
    # Get unique values for filters
    tourism_data = TourismData.objects.filter(uploaded_by=request.user)
    
    # Debug information
    data_count = tourism_data.count()
    print(f"Dashboard: Total records for user {request.user.username}: {data_count}")
    
    years = sorted(tourism_data.values_list('year', flat=True).distinct())
    regions = sorted(tourism_data.values_list('region', flat=True).distinct())
    visitor_types = sorted(tourism_data.values_list('visitor_type', flat=True).distinct())
    
    print(f"Dashboard: Years: {years}")
    print(f"Dashboard: Regions: {regions}")
    print(f"Dashboard: Visitor Types: {visitor_types}")
    
    context = {
        'default_view': user_dashboard.default_view,
        'custom_filters': user_dashboard.custom_filters,
        'custom_visualizations': custom_visualizations,
        'years': years,
        'regions': regions,
        'visitor_types': visitor_types,
    }
    return render(request, 'tourism_dashboard/dashboard.html', context)

@login_required
def upload_data(request):
    if request.method == 'POST':
        form = TourismDataUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                df = pd.read_csv(request.FILES['data_file'])
                print(f"Upload: CSV file loaded with {len(df)} rows")
                print(f"Upload: CSV columns: {df.columns.tolist()}")
                
                records_created = 0
                for _, row in df.iterrows():
                    TourismData.objects.create(
                        year=row['Year'],
                        country=row['Country'],
                        region=row['Region'],
                        visitor_count=row['Visitor_Count'],
                        visitor_type=row['Visitor_Type'],
                        season=row['Season'],
                        age_group=row['Age_Group'],
                        uploaded_by=request.user
                    )
                    records_created += 1
                
                print(f"Upload: Created {records_created} records in the database")
                messages.success(request, f'Data uploaded successfully! {records_created} records created.')
                return redirect('dashboard')
            except Exception as e:
                print(f"Upload: Error uploading data: {str(e)}")
                messages.error(request, f'Error uploading data: {str(e)}')
    else:
        form = TourismDataUploadForm()
    
    return render(request, 'tourism_dashboard/upload.html', {'form': form})

@login_required
def create_visualization(request):
    if request.method == 'POST':
        form = CustomVisualizationForm(request.POST)
        if form.is_valid():
            visualization = form.save(commit=False)
            visualization.user = request.user
            visualization.save()
            messages.success(request, 'Visualization created successfully!')
            return redirect('dashboard')
    else:
        form = CustomVisualizationForm()
    
    return render(request, 'tourism_dashboard/create_visualization.html', {'form': form})

@login_required
@require_POST
def update_dashboard_preferences(request):
    try:
        data = json.loads(request.body)
        user_dashboard = UserDashboard.objects.get(user=request.user)
        user_dashboard.default_view = data.get('default_view', user_dashboard.default_view)
        user_dashboard.custom_filters = data.get('custom_filters', user_dashboard.custom_filters)
        user_dashboard.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def delete_visualization(request, viz_id):
    try:
        visualization = CustomVisualization.objects.get(id=viz_id, user=request.user)
        visualization.delete()
        messages.success(request, 'Visualization deleted successfully!')
    except CustomVisualization.DoesNotExist:
        messages.error(request, 'Visualization not found!')
    return redirect('dashboard')

def get_visualization_data(request, view_type):
    # Get filter parameters
    year_range = request.GET.get('year_range', '')
    region = request.GET.get('region', '')
    visitor_type = request.GET.get('visitor_type', '')

    # Base queryset
    queryset = TourismData.objects.all()
    
    # Debug information
    total_count = queryset.count()
    print(f"Total records in database: {total_count}")

    # Apply filters
    if year_range:
        start_year, end_year = map(int, year_range.split('-'))
        queryset = queryset.filter(year__gte=start_year, year__lte=end_year)
    if region:
        queryset = queryset.filter(region=region)
    if visitor_type:
        queryset = queryset.filter(visitor_type=visitor_type)
    
    # Debug filtered count
    filtered_count = queryset.count()
    print(f"Filtered records: {filtered_count}")

    response_data = {}

    if view_type == 'yearly_trends':
        # Yearly trends visualization
        yearly_data = queryset.values('year').annotate(
            total_visitors=Sum('visitor_count')
        ).order_by('year')
        
        # Debug yearly data
        print(f"Yearly data points: {list(yearly_data)}")

        response_data['yearly_trends'] = {
            'data': [{
                'x': [d['year'] for d in yearly_data],
                'y': [d['total_visitors'] for d in yearly_data],
                'type': 'scatter',
                'mode': 'lines+markers',
                'name': 'Total Visitors'
            }],
            'layout': {
                'title': 'Yearly Tourism Trends',
                'xaxis': {'title': 'Year'},
                'yaxis': {'title': 'Number of Visitors'}
            }
        }

    elif view_type == 'regional_distribution':
        # Regional distribution visualization
        regional_data = queryset.values('region').annotate(
            total_visitors=Sum('visitor_count')
        ).order_by('-total_visitors')
        
        # Debug regional data
        print(f"Regional data points: {list(regional_data)}")

        response_data['regional_distribution'] = {
            'data': [{
                'labels': [d['region'] for d in regional_data],
                'values': [d['total_visitors'] for d in regional_data],
                'type': 'pie',
                'name': 'Regional Distribution'
            }],
            'layout': {
                'title': 'Regional Distribution of Visitors'
            }
        }

    elif view_type == 'demographics':
        # Demographics visualization
        demographics_data = queryset.values('visitor_type').annotate(
            total_visitors=Sum('visitor_count')
        ).order_by('-total_visitors')
        
        # Debug demographics data
        print(f"Demographics data points: {list(demographics_data)}")

        response_data['demographics'] = {
            'data': [{
                'x': [d['visitor_type'] for d in demographics_data],
                'y': [d['total_visitors'] for d in demographics_data],
                'type': 'bar',
                'name': 'Visitor Types'
            }],
            'layout': {
                'title': 'Visitor Demographics',
                'xaxis': {'title': 'Visitor Type'},
                'yaxis': {'title': 'Number of Visitors'}
            }
        }

    return JsonResponse(response_data)

def debug_data(request):
    """Debug view to check data in the database"""
    data_count = TourismData.objects.count()
    sample_data = list(TourismData.objects.all()[:5])
    
    return JsonResponse({
        'count': data_count,
        'sample': [
            {
                'year': item.year,
                'country': item.country,
                'region': item.region,
                'visitor_count': item.visitor_count,
                'visitor_type': item.visitor_type,
                'season': item.season,
                'age_group': item.age_group,
            } for item in sample_data
        ]
    })

@login_required
def export_data_for_tableau(request):
    """Export data to CSV format for Tableau"""
    # Get all tourism data for the current user
    tourism_data = TourismData.objects.filter(uploaded_by=request.user)
    
    # Create a CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Year', 'Country', 'Region', 'Visitor_Count', 'Visitor_Type', 'Season', 'Age_Group'])
    
    # Write data
    for item in tourism_data:
        writer.writerow([
            item.year,
            item.country,
            item.region,
            item.visitor_count,
            item.visitor_type,
            item.season,
            item.age_group
        ])
    
    # Prepare the response
    output.seek(0)
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tourism_data_for_tableau.csv"'
    
    return response

@login_required
def tableau_dashboard(request):
    """View for the Tableau dashboard page"""
    return render(request, 'tourism_dashboard/tableau_dashboard.html')

@csrf_exempt
def tableau_wdc(request):
    """Tableau Web Data Connector endpoint"""
    if request.method == 'GET':
        # Return the WDC HTML page
        return render(request, 'tourism_dashboard/tableau_wdc.html')
    elif request.method == 'POST':
        # Handle the data request from Tableau
        try:
            # Get the user's authentication token from the request
            auth_token = request.POST.get('auth_token', '')
            
            # In a real implementation, you would validate this token
            # and get the corresponding user
            
            # For now, we'll just return all data
            tourism_data = TourismData.objects.all()
            
            # Format the data for Tableau
            data = []
            for item in tourism_data:
                data.append({
                    'Year': item.year,
                    'Country': item.country,
                    'Region': item.region,
                    'Visitor_Count': item.visitor_count,
                    'Visitor_Type': item.visitor_type,
                    'Season': item.season,
                    'Age_Group': item.age_group
                })
            
            return JsonResponse({
                'data': data
            })
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500) 
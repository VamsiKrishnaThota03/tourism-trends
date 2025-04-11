from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload_data, name='upload_data'),
    path('create-visualization/', views.create_visualization, name='create_visualization'),
    path('update-preferences/', views.update_dashboard_preferences, name='update_preferences'),
    path('delete-visualization/<int:viz_id>/', views.delete_visualization, name='delete_visualization'),
    path('api/visualization/<str:view_type>/', views.get_visualization_data, name='visualization_data'),
    path('debug/data/', views.debug_data, name='debug_data'),
    path('export-tableau/', views.export_data_for_tableau, name='export_tableau'),
    path('tableau-dashboard/', views.tableau_dashboard, name='tableau_dashboard'),
    path('tableau-wdc/', views.tableau_wdc, name='tableau_wdc'),
] 
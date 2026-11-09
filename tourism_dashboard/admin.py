from django.contrib import admin

from .models import CustomVisualization, TourismData, UserDashboard


@admin.register(TourismData)
class TourismDataAdmin(admin.ModelAdmin):
    list_display = ('year', 'country', 'region', 'visitor_type', 'season', 'age_group',
                    'visitor_count', 'uploaded_by')
    list_filter = ('year', 'region', 'visitor_type', 'season')
    search_fields = ('country', 'region')


@admin.register(CustomVisualization)
class CustomVisualizationAdmin(admin.ModelAdmin):
    list_display = ('title', 'chart_type', 'user', 'created_at')


admin.site.register(UserDashboard)

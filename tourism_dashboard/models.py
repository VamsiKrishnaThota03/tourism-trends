from django.db import models
from django.contrib.auth.models import User

class TourismData(models.Model):
    year = models.IntegerField()
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    visitor_count = models.IntegerField()
    visitor_type = models.CharField(max_length=50)
    season = models.CharField(max_length=50)
    age_group = models.CharField(max_length=50)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year', 'country']

    def __str__(self):
        return f"{self.country} - {self.year}"

class UserDashboard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_view = models.CharField(max_length=50, default='yearly_trends')
    custom_filters = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Dashboard"

class CustomVisualization(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    chart_type = models.CharField(max_length=50)
    data_filters = models.JSONField()
    chart_config = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title 
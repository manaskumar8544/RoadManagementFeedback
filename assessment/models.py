from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class PavementAssessment(models.Model):
    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('critical', 'Critical'),
    ]
    
    DISTRESS_TYPES = [
        ('none', 'No Distress'),
        ('transverse', 'Transverse Crack'),
        ('longitudinal', 'Longitudinal Crack'),
        ('alligator', 'Alligator Crack'),
        ('pothole', 'Pothole'),
        ('multiple', 'Multiple Distress Types'),
    ]
    
    # User and Image fields
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='uploads/pavement/')
    uploaded_at = models.DateTimeField(default=timezone.now)
    
    # Assessment Results
    overall_condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, blank=True)
    distress_type = models.CharField(max_length=20, choices=DISTRESS_TYPES, default='none')
    severity_score = models.FloatField(default=0.0)  # 0-100 scale
    crack_density = models.FloatField(default=0.0)   # Percentage
    confidence_level = models.FloatField(default=0.0)  # 0-100 scale
    
    # Additional metadata
    location = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    ai_description = models.TextField(blank=True, help_text="AI-generated description")
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        
    def __str__(self):
        return f"Assessment {self.id} - {self.overall_condition} ({self.uploaded_at.strftime('%Y-%m-%d')})"
    
    def get_condition_color(self):
        """Return color code for condition status"""
        colors = {
            'excellent': '#10b981',
            'good': '#3b82f6',
            'fair': '#f59e0b',
            'poor': '#ef4444',
            'critical': '#991b1b',
        }
        return colors.get(self.overall_condition, '#6b7280')

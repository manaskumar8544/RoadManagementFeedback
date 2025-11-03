from django.contrib import admin
from .models import PavementAssessment

@admin.register(PavementAssessment)
class PavementAssessmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'overall_condition', 'distress_type', 
                    'severity_score', 'uploaded_at', 'processed']
    list_filter = ['overall_condition', 'distress_type', 'processed', 'uploaded_at']
    search_fields = ['location', 'notes']
    readonly_fields = ['uploaded_at', 'processed_at']
    date_hierarchy = 'uploaded_at'
    
    fieldsets = (
        ('Image Information', {
            'fields': ('user', 'image', 'uploaded_at', 'location', 'notes')
        }),
        ('Assessment Results', {
            'fields': ('overall_condition', 'distress_type', 'severity_score', 
                      'crack_density', 'confidence_level', 'processed', 'processed_at')
        }),
    )

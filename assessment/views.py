from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import PavementAssessment
from .forms import PavementUploadForm
from .utils import analyze_pavement_image

def home(request):
    """Home page"""
    recent_assessments = PavementAssessment.objects.all()[:6]
    context = {
        'recent_assessments': recent_assessments,
    }
    return render(request, 'assessment/home.html', context)

def upload_image(request):
    """Upload and analyze pavement image"""
    if request.method == 'POST':
        form = PavementUploadForm(request.POST, request.FILES)
        if form.is_valid():
            assessment = form.save(commit=False)
            
            # Associate with user if logged in
            if request.user.is_authenticated:
                assessment.user = request.user
            
            assessment.save()
            
            # Analyze the image
            analysis_results = analyze_pavement_image(assessment.image.path)
            
            # Update assessment with results
            for key, value in analysis_results.items():
                setattr(assessment, key, value)
            assessment.save()
            
            messages.success(request, 'Image uploaded and analyzed successfully!')
            return redirect('assessment_results', pk=assessment.pk)
    else:
        form = PavementUploadForm()
    
    return render(request, 'assessment/upload.html', {'form': form})

def assessment_results(request, pk):
    """Display assessment results"""
    assessment = get_object_or_404(PavementAssessment, pk=pk)
    context = {
        'assessment': assessment,
    }
    return render(request, 'assessment/results.html', context)

def assessment_history(request):
    """Display all assessments"""
    assessments = PavementAssessment.objects.all()
    
    # Pagination
    paginator = Paginator(assessments, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'assessment/history.html', context)

def delete_assessment(request, pk):
    """Delete assessment"""
    assessment = get_object_or_404(PavementAssessment, pk=pk)
    
    if request.method == 'POST':
        # Delete the image file
        if assessment.image:
            assessment.image.delete()
        assessment.delete()
        messages.success(request, 'Assessment deleted successfully!')
        return redirect('assessment_history')
    
    return redirect('assessment_results', pk=pk)

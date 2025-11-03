from django import forms
from .models import PavementAssessment

class PavementUploadForm(forms.ModelForm):
    class Meta:
        model = PavementAssessment
        fields = ['image', 'location', 'notes']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*',
                'id': 'image-upload'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter location (optional)',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Add any notes about the pavement condition...',
                'rows': 3,
            }),
        }
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check file size (max 10MB)
            if image.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Image file too large ( > 10MB )")
            
            # Check file extension
            allowed_extensions = ['jpg', 'jpeg', 'png', 'bmp']
            ext = image.name.split('.')[-1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError(f"File type not supported. Allowed: {', '.join(allowed_extensions)}")
        
        return image

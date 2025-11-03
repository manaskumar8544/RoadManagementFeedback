import google.generativeai as genai
from PIL import Image
from django.utils import timezone
from decouple import config
import json
import re

GEMINI_API_KEY = config('GEMINI_API_KEY', default='')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_vision_model_names():
    """Returns a list of current, vision-capable models to try in order."""
    # This list is updated to use current, vision-capable models
    return [
        'gemini-2.5-pro',    # Latest powerful vision model
        'gemini-2.5-flash',  # Latest fast vision model
        'gemini-pro',        # Alias for the latest stable model
    ]

def analyze_pavement_image(image_path):
    try:
        if not GEMINI_API_KEY:
            print("Warning: Gemini API key not found.")
            return get_default_results()
        
        img = Image.open(image_path)
        model_names = get_vision_model_names()
        
        if not model_names:
            print("No models to try.")
            return get_default_results()

        prompt = "Analyze this pavement image as a civil engineer. Provide assessment in JSON format with these exact keys: overall_condition (must be: excellent, good, fair, poor, or critical), distress_type (must be: none, transverse, longitudinal, alligator, pothole, or multiple), severity_score (0-100), crack_density (0-100), confidence_level (0-100). Return only valid JSON, no extra text."
        
        # Loop through each model and try to get a response
        for model_name in model_names:
            try:
                print(f"Attempting to use model: {model_name}")
                model = genai.GenerativeModel(model_name)
                
                # The actual API call is inside the loop
                response = model.generate_content([prompt, img])
                print("Gemini Response:", response.text)
                
                # If we get here, the call was successful
                result = parse_gemini_response(response.text)
                result['processed'] = True
                result['processed_at'] = timezone.now()
                return result # Success! Break the loop and return.
                
            except Exception as e:
                # This will catch 404s, permission errors, etc.
                print(f"Model {model_name} failed: {str(e)}")
                continue # Try the next model in the list
        
        # If we get through the whole loop without returning
        print("All available Gemini vision models failed.")
        return get_default_results()
    
    except Exception as e:
        # This catches other errors (e.g., Image.open() failing)
        print("Error in analyze_pavement_image:", str(e))
        return get_default_results()

def parse_gemini_response(response_text):
    try:
        clean_text = response_text.strip()
        # Remove markdown code fences
        clean_text = re.sub(r'^```json\n', '', clean_text, flags=re.MULTILINE)
        clean_text = re.sub(r'\n```$', '', clean_text, flags=re.MULTILINE)
        clean_text = clean_text.replace('``````', '') # Handle other fence types
        
        # Be more flexible with finding the JSON object
        match = re.search(r'\{.*\}', clean_text, re.DOTALL)
        
        if match:
            json_str = match.group(0)
            data = json.loads(json_str)
            
            return {
                'overall_condition': validate_condition(data.get('overall_condition', 'fair')),
                'distress_type': validate_distress(data.get('distress_type', 'none')),
                'severity_score': float(data.get('severity_score', 50.0)),
                'crack_density': float(data.get('crack_density', 0.0)),
                'confidence_level': float(data.get('confidence_level', 70.0)),
            }
        else:
            print("No JSON object found, falling back to text extraction.")
            return extract_values_from_text(response_text)
    
    except Exception as e:
        print(f"Parse error: {e}. Falling back to text extraction.")
        # If JSON parsing fails, try to get *something* from the text
        return extract_values_from_text(response_text)

def extract_values_from_text(text):
    print("Extracting values directly from text...")
    result = {
        'overall_condition': 'fair',
        'distress_type': 'none',
        'severity_score': 50.0,
        'crack_density': 0.0,
        'confidence_level': 70.0,
    }
    
    text_lower = text.lower()
    
    for condition in ['critical', 'poor', 'fair', 'good', 'excellent']:
        if condition in text_lower:
            result['overall_condition'] = condition
            break
    
    for distress in ['pothole', 'alligator', 'longitudinal', 'transverse', 'multiple', 'none']:
        if distress in text_lower:
            result['distress_type'] = distress
            break
    
    # Try to find numbers associated with keys
    severity_match = re.search(r'["\']?severity_score["\']?\s*[:=]\s*(\d+\.?\d*)', text_lower)
    crack_match = re.search(r'["\']?crack_density["\']?\s*[:=]\s*(\d+\.?\d*)', text_lower)
    confidence_match = re.search(r'["\']?confidence_level["\']?\s*[:=]\s*(\d+\.?\d*)', text_lower)
    
    if severity_match:
        result['severity_score'] = float(severity_match.group(1))
    if crack_match:
        result['crack_density'] = float(crack_match.group(1))
    if confidence_match:
        result['confidence_level'] = float(confidence_match.group(1))
    
    return result

def validate_condition(condition):
    valid = ['excellent', 'good', 'fair', 'poor', 'critical']
    condition = str(condition).lower().strip()
    return condition if condition in valid else 'fair'

def validate_distress(distress):
    valid = ['none', 'transverse', 'longitudinal', 'alligator', 'pothole', 'multiple']
    distress = str(distress).lower().strip()
    return distress if distress in valid else 'none'

def get_default_results():
    return {
        'overall_condition': 'fair',
        'distress_type': 'none',
        'severity_score': 50.0,
        'crack_density': 0.0,
        'confidence_level': 60.0,
        'processed': True,
        'processed_at': timezone.now()
    }
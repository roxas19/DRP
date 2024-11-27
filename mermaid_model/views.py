from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from PIL import Image
import pytesseract
import os

# Configure Tesseract paths
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'  # Adjust if needed
os.environ['TESSDATA_PREFIX'] = '/opt/homebrew/share/tessdata/'  # Ensure this points to tessdata

@csrf_exempt
@require_POST
def upload_pdf_page(request):
    try:
        uploaded_file = request.FILES.get('page')

        if not uploaded_file:
            return JsonResponse({'error': 'No file received'}, status=400)

        # Save the file temporarily
        temp_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
        with open(temp_path, 'wb') as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)

        # Open the image using PIL
        image = Image.open(temp_path)

        # Perform OCR with Tamil language
        extracted_text = pytesseract.image_to_string(image, lang='Tamil')

        # Log the extracted text to the console
        print("Extracted Text:")
        print(extracted_text)

        # Clean up the temporary file
        os.remove(temp_path)

        # For now, just return a success message without sending the text back
        return JsonResponse({'message': 'Text extracted and logged successfully'})
    except Exception as e:
        print(f"Error handling file: {e}")
        return JsonResponse({'error': 'Failed to process file'}, status=500)

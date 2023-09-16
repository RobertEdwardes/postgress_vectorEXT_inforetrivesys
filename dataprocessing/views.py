import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from .forms import FileUploadForm
from .models import FileUpload, Files
from dataprocessing.tasks import text_to_embed
from django.contrib import messages

import fitz 
from docx import Document
import os
import nltk
from nltk.tokenize import sent_tokenize
nltk.download('punkt')
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

import logging

logger = logging.getLogger('file')

# Create your views here.
@login_required
def bulk_upload(request):
    if request.method == 'POST':
        try:
            form = FileUploadForm(request.POST, request.FILES)
            if form.is_valid():
                files = request.FILES.getlist('file')
                logger.info(f'user ID: {request.user.id} --- files uploaded: {len(files)} ')
                for file in files:
                    try:
                        instance = FileUpload(file=file)
                        instance.save()  
                        instance.file_path = instance.file.url  
                        instance.save()
                    except Exception as e:
                        logging.warn(f'user ID: {request.user.id} --- {file} save process FAILED --- {str(e)}')
                        messages.warning(request, 'Upload process FAILED')  
        except Exception as e:
            logging.error(f'user ID: {request.user.id} --- Upload process FAILED --- {str(e)}')
            messages.error(request, 'Upload process FAILED')
          
    else:
        form = FileUploadForm()
    return render(request, 'upload.html', {'form': form})
@login_required
def view_uploads(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        selected_records = request.POST.getlist('selected_records')

        if action == 'delete':
            logger.info(f'user ID: {request.user.id} --- deleted: {len(selected_records)} ')
            delete_selected_records(selected_records, request)
            return redirect('view_uploads') 
        elif action == 'process':
            logger.info(f'user ID: {request.user.id} --- processing: {len(selected_records)}')
            process_selected_records(selected_records, request)
            return redirect('view_uploads') 

    file_list = FileUpload.objects.all().order_by('-uploaded_at')
    paginator = Paginator(file_list, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'file_upload_list.html', {'page_obj': page_obj})

def delete_selected_records(selected_ids, request):
    for id in selected_ids:
        try:
            file_upload = FileUpload.objects.get(id=id)
            file_path = file_upload.file.path 

            if os.path.exists(file_path):
                os.remove(file_path)

            file_upload.delete()
            logger.info(f'User ID : {request.user.id} --- Deleted File Path : {file_path}')
        except FileUpload.DoesNotExist:
            logger.error(f'Missing file --- file ID: {id} --- Location: {file_path}')

async def process_selected_records(selected_ids, request):
    for id in selected_ids:
        result = text_to_embed.delay(id)
        logger.debug(result)
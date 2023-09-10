import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from .forms import FileUploadForm
from .models import FileUpload, Files
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

def process_selected_records(selected_ids, request):
    user_id = str(request.user.id)
    for id in selected_ids:
        try:
            file_upload = FileUpload.objects.get(id=id, processed=False)
        except FileUpload.DoesNotExist:
            continue
        file_extension = os.path.splitext(file_upload.file.name)[1].lower()
        if file_extension == '.pdf':
            text = pdf_to_text(file_upload.file.path)  
        elif file_extension == '.txt':
            text = txt_to_string(file_upload.file.path)  
        elif file_extension == '.docx':
            text = docx_to_text(file_upload.file.path)  
        else:
            logger.warn(f'file type not supported --- ID: {id} --- Name: {file_upload.file.name}')
            messages.warning(request,f'file type not supported Name: {file_upload.file.name}')
            continue

        logger.debug(f'file ID : {id} --- First 100 char : {text[:100]} --- Last 100 char : {text[-100:]}')    
        
        sentences = sent_tokenize(text)

        for sentence_pos, sentence_text in enumerate(sentences):

            embed_text = model.encode(sentence_text)
            Files.objects.create(
                idx_file=file_upload,
                sentence_pos=sentence_pos,
                sentence_text=sentence_text,
                sentence_embed=embed_text
            )
        file_upload.processed = True
        logger.info(f'User ID : {request.user.id} --- processed : {file_upload.file.path} --- sentence count : {len(sentences)}')
        file_upload.save()

def pdf_to_text(pdf_file_path):
    try:
        doc = fitz.open(pdf_file_path)
        text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text += page.get_text()
        return text
    except Exception as e:
        logging.error(f'PDF to String --- {str(e)}')

def txt_to_string(txt_file_path):
    try:
        with open(txt_file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text
    except Exception as e:
        logging.error(f'Text to String --- {str(e)}')

def docx_to_text(docx_file_path):
    try:
        doc = Document(docx_file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text
        return text
    except Exception as e:
        logging.error(f'Docx to String --- {str(e)}')
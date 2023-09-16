from celery import shared_task
from dataprocessing.models import FileUpload, Files

import fitz 
from docx import Document
import os
import nltk
from nltk.tokenize import sent_tokenize
nltk.download('punkt')
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')


@shared_task
def text_to_embed(id):
    try:
        file_upload = FileUpload.objects.get(id=id, processed=False)
    except FileUpload.DoesNotExist:
        return
    file_extension = os.path.splitext(file_upload.file.name)[1].lower()
    if file_extension == '.pdf':
        text = pdf_to_text(file_upload.file.path)  
    elif file_extension == '.txt':
        text = txt_to_string(file_upload.file.path)  
    elif file_extension == '.docx':
        text = docx_to_text(file_upload.file.path)  
    else:
        return

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
    file_upload.save()

def pdf_to_text(pdf_file_path):
    doc = fitz.open(pdf_file_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

def txt_to_string(txt_file_path):
    with open(txt_file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def docx_to_text(docx_file_path):
    doc = Document(docx_file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text
    return text

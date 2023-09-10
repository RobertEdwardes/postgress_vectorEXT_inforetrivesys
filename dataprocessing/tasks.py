from celery import shared_task
from dataprocessing.models import FileUpload, Files
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

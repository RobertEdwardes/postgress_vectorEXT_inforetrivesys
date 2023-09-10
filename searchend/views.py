from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import SearchForm
from sentence_transformers import SentenceTransformer
from dataprocessing.models import FileUpload, Files
from pgvector.django import L2Distance, CosineDistance, MaxInnerProduct 
model = SentenceTransformer('all-MiniLM-L6-v2')

import logging

logger = logging.getLogger('file')
# Create your views here.
@login_required
def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data.get('query', '')
            search_function = form.cleaned_data.get('search_function', 'L2Distance')
            query_count = form.cleaned_data.get('max_return')
            logger.info(f'user : {request.user.id} --- query : {query} --- search : {search_function} --- returns : {query_count}')
            _query = model.encode(query)
            if search_function == 'L2Distance':
                results = group_by_L2Distance(_query, query_count)
            elif search_function == 'MaxInnerProduct':
                results = group_by_MaxInnerProduct(_query, query_count)
            elif search_function == 'CosineDistance':
                results = group_by_CosineDistance(_query, query_count)
            else:
                results = []

            return render(request, 'search_results.html', {'results': results, 'query': query})
    else:
        form = SearchForm()
    return render(request, 'search_form.html', {'form': form})

def group_by_L2Distance(query, count):
    results = Files.objects.order_by(L2Distance('sentence_embed', query))[:count]
    data_list = []  
    for result in results:
        file_name = result.idx_file.file_name
        if file_name not in data_list:
            data_list.append(file_name) 
    return data_list
def group_by_MaxInnerProduct(query, count):
    results = Files.objects.order_by(MaxInnerProduct('sentence_embed', query))[:count]
    data_list = []  
    for result in results:
        file_name = result.idx_file.file_name
        if file_name not in data_list:
            data_list.append(file_name) 
    return data_list
def group_by_CosineDistance(query, count):
    results = Files.objects.order_by(CosineDistance('sentence_embed', query))[:count]
    data_list = []  
    for result in results:
        file_name = result.idx_file.file_name
        if file_name not in data_list:
            data_list.append(file_name) 
    return data_list
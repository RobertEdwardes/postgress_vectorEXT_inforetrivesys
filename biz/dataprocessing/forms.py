# forms.py
from django import forms
from django.forms.widgets import ClearableFileInput
from .models import FileUpload

class MultiFileInput(ClearableFileInput):
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['attrs']['multiple'] = True
        return context

class FileUploadForm(forms.ModelForm):
    file = forms.FileField(widget=MultiFileInput)

    class Meta:
        model = FileUpload
        fields = ('file',)

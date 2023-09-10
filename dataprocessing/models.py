from django.db import models
from pgvector.django import VectorField

# Create your models here.
class FileUpload(models.Model):
    file = models.FileField(upload_to='uploads/')
    file_path = models.CharField(max_length=255)
    file_name = models.TextField()
    processed = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.file_name: 
            self.file_name = self.file.name
        super(FileUpload, self).save(*args, **kwargs)

class Files(models.Model):
    idx_file = models.ForeignKey(FileUpload , on_delete=models.CASCADE)
    sentence_pos = models.IntegerField()
    sentence_text = models.TextField()
    sentence_embed = VectorField(dimensions=384)
# Generated by Django 3.2.21 on 2023-09-09 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataprocessing', '0004_alter_files_sentence_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileupload',
            name='file_name',
            field=models.TextField(default='OLD CHECK PATH'),
            preserve_default=False,
        ),
    ]

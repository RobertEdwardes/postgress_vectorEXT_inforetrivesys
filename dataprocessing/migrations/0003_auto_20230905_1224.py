# Generated by Django 3.2.21 on 2023-09-05 12:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataprocessing', '0002_alter_fileupload_processed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='files',
            name='page_num',
        ),
        migrations.RemoveField(
            model_name='files',
            name='paragraph_num',
        ),
    ]

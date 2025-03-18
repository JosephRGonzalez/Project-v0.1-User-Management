# Generated by Django 5.1.6 on 2025-03-18 17:10

import usr_mgmt_app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usr_mgmt_app', '0004_approvalrequest_pdf_document_userprofile_signature'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='signature',
            field=models.ImageField(blank=True, null=True, upload_to='signatures/', validators=[usr_mgmt_app.models.validate_signature_file]),
        ),
    ]

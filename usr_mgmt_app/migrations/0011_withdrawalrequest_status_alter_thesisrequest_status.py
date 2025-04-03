# Generated by Django 5.1.6 on 2025-04-03 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usr_mgmt_app', '0010_remove_withdrawalrequest_address_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='withdrawalrequest',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('pending', 'Pending'), ('returned', 'Returned'), ('approved', 'Approved')], default='Draft', max_length=20),
        ),
        migrations.AlterField(
            model_name='thesisrequest',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('pending', 'Pending'), ('returned', 'Returned'), ('approved', 'Approved')], default='Draft', max_length=20),
        ),
    ]

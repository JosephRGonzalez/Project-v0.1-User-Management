# Generated by Django 5.1.6 on 2025-04-18 00:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usr_mgmt_app', '0021_alter_userprofile_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='profile_banner',
            field=models.ImageField(blank=True, null=True, upload_to='banner_pictures/'),
        ),
    ]

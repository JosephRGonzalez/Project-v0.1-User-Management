# Generated by Django 5.1.6 on 2025-04-21 20:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usr_mgmt_app', '0022_userprofile_profile_banner'),
    ]

    operations = [
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('code', models.SlugField(unique=True)),
                ('is_college', models.BooleanField(default=False)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sub_units', to='usr_mgmt_app.unit')),
            ],
        ),
        migrations.AddField(
            model_name='userprofile',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='usr_mgmt_app.unit'),
        ),
    ]

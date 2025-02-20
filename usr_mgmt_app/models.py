from django.contrib.auth.models import AbstractUser
from django.db import models

class UserProfile(AbstractUser):
    ROLES = (
        ('admin', 'Administrator'),
        ('basicuser', 'Basic User'),
    )
    
    STATUS = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    
    role = models.CharField(max_length=20, choices=ROLES, default='basicuser')
    status = models.CharField(max_length=20, choices=STATUS, default='active')
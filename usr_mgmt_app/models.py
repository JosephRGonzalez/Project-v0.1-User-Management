from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class UserProfile(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('user', 'User'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    groups = models.ManyToManyField(Group, related_name="userprofile_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="userprofile_permissions", blank=True)

    class Meta:
        permissions = [
            ("can_read", "Can read data"),
            ("can_edit", "Can edit data"),
            ("can_manage_users", "Can activate/deactivate and delete users"),
        ]

    def __str__(self):
        return f"{self.username} ({self.role})"

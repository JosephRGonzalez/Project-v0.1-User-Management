from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from .models import UserProfile

@receiver(post_save, sender=UserProfile)
def assign_permissions(sender, instance, created, **kwargs):
    """Automatically assign permissions when a user is created or updated."""
    if created:  # Only assign permissions for new users
        if instance.role == 'admin':
            # Admin gets all permissions
            admin_permissions = Permission.objects.all()
            instance.user_permissions.set(admin_permissions)
        elif instance.role == 'moderator':
            # Moderator gets read and edit permissions
            moderator_permissions = Permission.objects.filter(codename__in=['can_read', 'can_edit'])
            instance.user_permissions.set(moderator_permissions)
        elif instance.role == 'user':
            # User gets only read permissions
            user_permissions = Permission.objects.filter(codename='can_read')
            instance.user_permissions.set(user_permissions)

        # Save the instance again to update user_permissions
        instance.save()

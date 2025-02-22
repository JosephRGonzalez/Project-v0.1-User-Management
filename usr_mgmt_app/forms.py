from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'role', 'is_active' , 'password']

# Override save method to use email as username
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email  # Use email as username
        # Hash the password before saving
        if user.password:
            user.set_password(user.password)

        if commit:
            user.save()
        return user

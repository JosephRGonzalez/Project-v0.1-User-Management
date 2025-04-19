from django import forms
from django.contrib.auth.forms import PasswordChangeForm
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


class PublicProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'profile_picture',
            'profile_banner',
            'major',
            'college',
            'academic_level',
            'bio',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'placeholder': 'Write a short bio...'}),
            'major': forms.TextInput(attrs={'placeholder': 'e.g. Computer Science'}),
        }


class EmailUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'you@example.com'})
        }


class CougarIDUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['cougar_id']
        widgets = {
            'cougar_id': forms.TextInput(attrs={'placeholder': '7-digit Cougar ID'})
        }

    def clean_cougar_id(self):
        cougar_id = self.cleaned_data.get('cougar_id')
        if not cougar_id.isdigit() or len(cougar_id) != 7:
            raise forms.ValidationError("Cougar ID must be exactly 7 digits.")
        return cougar_id


class ConfirmDeleteAccountForm(forms.Form):
    password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}),
    )
    confirm_text = forms.CharField(
        label="Type DELETE to confirm",
        max_length=6,
        widget=forms.TextInput(attrs={'placeholder': 'Type DELETE'})
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise forms.ValidationError("Incorrect password.")
        return password

    def clean_confirm_text(self):
        confirm = self.cleaned_data.get('confirm_text')
        if confirm.strip().upper() != 'DELETE':
            raise forms.ValidationError("You must type DELETE exactly to confirm.")
        return confirm


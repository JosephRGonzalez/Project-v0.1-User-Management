from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import UserProfile
from django import forms

# Form for creating/editing users
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'status']

# Check if user is admin
def is_admin(user):
    return user.role == 'admin'

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if user.status == 'active':
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Your account is inactive.')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'index.html')  # Changed from usr_mgmt_app/index.html

# Logout view
def logout_view(request):
    logout(request)
    return redirect('login')

# Dashboard view
@login_required
def dashboard_view(request):
    admin_count = UserProfile.objects.filter(role='admin').count()
    user_count = UserProfile.objects.filter(role='basicuser').count()
    
    context = {
        'admin_count': admin_count,
        'user_count': user_count,
    }
    
    return render(request, 'dashboard.html', context)  # Changed from usr_mgmt_app/dashboard.html

# User list view
@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = UserProfile.objects.all()
    return render(request, 'users.html', {'users': users})  # Changed from usr_mgmt_app/users.html

# User create view
@login_required
@user_passes_test(is_admin)
def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data['password']:
                user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'User created successfully.')
            return redirect('user_list')
    else:
        form = UserForm()
    
    return render(request, 'user_form.html', {'form': form, 'action': 'Create'})  # Changed path

# User edit view
@login_required
@user_passes_test(is_admin)
def user_edit(request, user_id):
    user = get_object_or_404(UserProfile, id=user_id)
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data['password']:
                user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'User updated successfully.')
            return redirect('user_list')
    else:
        form = UserForm(instance=user)
    
    return render(request, 'user_form.html', {'form': form, 'action': 'Edit'})  # Changed path

# User delete view
@login_required
@user_passes_test(is_admin)
def user_delete(request, user_id):
    user = get_object_or_404(UserProfile, id=user_id)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('user_list')
    
    return render(request, 'user_confirm_delete.html', {'user': user})  # Changed path

# User deactivate view
@login_required
@user_passes_test(is_admin)
def user_deactivate(request, user_id):
    user = get_object_or_404(UserProfile, id=user_id)
    
    if request.method == 'POST':
        user.status = 'inactive'
        user.save()
        messages.success(request, 'User deactivated successfully.')
        return redirect('user_list')
    
    return render(request, 'user_confirm_deactivate.html', {'user': user})  # Changed path
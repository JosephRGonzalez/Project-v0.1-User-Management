from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import logout
from .models import UserProfile
from .forms import UserProfileForm
from django.contrib.auth.decorators import permission_required




#Login/Home Page (index.html)
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to a dashboard after login
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'index.html')  # Render login page





# Redirects user to Dashboard (dashboard.html) after logging in
@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')

def dashboard_view(request):
    # Get the count of Admins and Users
    admin_count = UserProfile.objects.filter(role='admin').count()
    moderator_count = UserProfile.objects.filter(role='moderator').count()
    user_count = UserProfile.objects.filter(role='user').count()


    # Render the dashboard template with the counts
    return render(request, 'dashboard.html', {
        'admin_count': admin_count,
        'moderator_count': moderator_count,
        'user_count': user_count,
    })



# Sign up form (signup.html)
def signup_view(request):
    if request.method == 'POST':
        # Getting data from the form
        first_name = request.POST['f-name']
        last_name = request.POST['l-name']
        email = request.POST['mail']
        password = request.POST['user-password']
        password_confirm = request.POST['user-password-confirm']

        # Validation for matching passwords
        if password != password_confirm:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')

        # Check if the email already exists
        if UserProfile.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect('signup')

        # Create the user
        user = UserProfile.objects.create_user(
            username=email,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )
        user.save()

        # Redirect to a login page or home page after successful signup
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')

    return render(request, 'signup.html')

@login_required
def dashboard(request):
    # Count the number of admins and users
    admin_count = User.objects.filter(userprofile__role='admin').count()
    moderator_count = User.objects.filter(userprofile__role='moderator').count()
    user_count = User.objects.filter(userprofile__role='user').count()

    # Pass the counts to the template
    context = {
        'admin_count': admin_count,
        'moderator_count': moderator_count,
        'user_count': user_count,
    }
    return render(request, 'dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout


@login_required
@permission_required('usr_mgmt_app.can_read', raise_exception=True)
def user_list(request):
    users = UserProfile.objects.all()
    # Get the permissions for the current user
    has_edit_permission = request.user.has_perm('usr_mgmt_app.can_edit')
    has_manage_users_permission = request.user.has_perm('usr_mgmt_app.can_manage_users')

    # Add permissions to context
    context = {
        'has_edit_permission': has_edit_permission,
        'has_manage_users_permission': has_manage_users_permission,
        'users': UserProfile.objects.all(),  # Assuming you have users in your context
    }

    return render(request, 'user_list.html', {
        'users': users,
        'has_edit_permission': has_edit_permission,
        'has_manage_users_permission': has_manage_users_permission
    })




########## ADMIN PRIVILEGES


#Creating a user (ADMIN ONLY)
@permission_required('usr_mgmt_app.can_manage_users', raise_exception=True)
def user_create(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserProfileForm()
    return render(request, 'user_create.html', {'form': form})


# Edit a user (ADMIN AND MODERATORS ONLY)
@permission_required('usr_mgmt_app.can_edit', raise_exception=True)
def user_edit(request, user_id):  # Use user_id instead of id
    user = get_object_or_404(UserProfile, id=user_id)  # Fetch the user by user_id

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'user_edit.html', {'form': form, 'user': user})


# Deactivate a user (ADMIN ONLY)

@permission_required('usr_mgmt_app.can_manage_users', raise_exception=True)
def user_deactivate(request, id):
    user = get_object_or_404(UserProfile, id=id)
    user.is_active = False
    user.save()
    return redirect('user_list')

# Delete a user (ADMIN ONLY)
@permission_required('usr_mgmt_app.can_manage_users', raise_exception=True)
def user_delete(request, id):
    user = get_object_or_404(UserProfile, id=id)
    user.delete()
    return redirect('user_list')

# Toggles between Activating and Deactivating a user
def user_toggle_status(request, user_id):
    user = get_object_or_404(UserProfile, id=user_id)
    user.is_active = not user.is_active  # Toggle the is_active status
    user.save()
    return redirect('user_list')

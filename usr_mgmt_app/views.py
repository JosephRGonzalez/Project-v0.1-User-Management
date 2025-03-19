from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import logout
from .models import UserProfile, ApprovalRequest, ApprovalStep  # Updated to include new models
from .forms import UserProfileForm
from django.contrib.auth.decorators import permission_required
import os



#Landing Page
def landing_page(request):
    return render(request, 'landing_page.html')


#Login Page (index.html)
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
def user_edit(request, user_id):
    user = get_object_or_404(UserProfile, id=user_id)

    if request.method == "POST":
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.email = request.POST.get("email", user.email)
        user.role = request.POST.get("role", user.role)

        user.save()  # Save changes to the database

        return redirect("user_list")  # Redirect to user list after saving

    return render(request, "user_edit.html", {"user": user})


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


########## APPROVAL SYSTEM ##########
from .utils import generate_approval_pdf

@login_required
def approve_request_view(request, step_id):
    """View for approving a request"""
    # Get the approval step that belongs to this approver
    step = get_object_or_404(ApprovalStep, id=step_id, approver=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        comment = request.POST.get('comment', '')
        
        if action == 'approve':
            # Mark this approval step as approved
            step.status = 'approved'
            step.comments = comment
            step.save()
            
            # Check if all steps are approved
            all_steps = ApprovalStep.objects.filter(request=step.request)
            all_approved = all(s.status == 'approved' for s in all_steps)
            
            if all_approved:
                # If all approvers have approved, update the main request status
                step.request.status = 'approved'
                step.request.save()
                
                # Generate PDF for the approved request
                try:
                    pdf_path = generate_approval_pdf(step.request.id)
                    if pdf_path:
                        step.request.pdf_document = pdf_path
                        step.request.save()
                        messages.success(request, "Request approved and PDF generated successfully.")
                    else:
                        messages.success(request, "Request approved successfully, but PDF generation failed.")
                except Exception as e:
                    messages.success(request, f"Request approved successfully, but PDF generation error: {str(e)}")
            else:
                messages.success(request, "Request approved successfully. Awaiting other approvers.")
        
        elif action == 'return':
            # Mark this step as returned
            step.status = 'returned'
            step.comments = comment
            step.save()
            
            # Update the main request status to returned
            step.request.status = 'returned'
            step.request.save()
            
            messages.success(request, "Request returned for revisions.")
        
        return redirect('approval_requests')
    
    # If not a POST request, show the approval form
    return render(request, 'approve_request.html', {'step': step})
@login_required
def approval_requests_view(request):
    # Get all approval requests made by the current user
    try:
        user_requests = ApprovalRequest.objects.filter(requester=request.user).order_by('-created_at')
        
        # If the user is an approver, get pending requests assigned to them
        if request.user.role in ['admin', 'moderator']:
            pending_approvals = ApprovalStep.objects.filter(
                approver=request.user, 
                status='pending'
            ).select_related('request')
        else:
            pending_approvals = None
        
        # Get ETD forms for this user
        etd_forms = ETDForm.objects.filter(student=request.user).order_by('-created_at')
        
        context = {
            'user_requests': user_requests,
            'pending_approvals': pending_approvals,
            'etd_forms': etd_forms
        }
    except Exception as e:
        # If models are not yet available, use an empty context
        print(f"Error in approval_requests_view: {str(e)}")
        context = {}
    
    return render(request, 'approval_requests.html', context)
from .utils import generate_etd_form

@login_required
def create_etd_form_view(request):
    """View for creating an ETD form"""
    if request.method == 'POST':
        # Process form submission
        student_id_number = request.POST.get('student_id_number')
        degree_type = request.POST.get('degree_type')
        graduation_date = request.POST.get('graduation_date')
        request_type = request.POST.get('request_type')
        justification = request.POST.get('justification')
        
        try:
            # Create ETD form
            etd_form = ETDForm.objects.create(
                student=request.user,
                student_id_number=student_id_number,
                degree_type=degree_type,
                graduation_date=graduation_date,
                request_type=request_type,
                justification=justification,
                status='pending'
            )
            
            # Generate PDF for the form
            form_data = {
                'student_id': student_id_number,
                'degree_type': etd_form.get_degree_type_display(),
                'graduation_date': graduation_date,
                'justification': justification,
            }
            
            pdf_path = generate_etd_form(request.user.id, form_data)
            if pdf_path:
                etd_form.pdf_document = pdf_path
                etd_form.save()
                messages.success(request, "ETD form created successfully. You can download it from the list below.")
            else:
                messages.warning(request, "ETD form created but PDF generation failed.")
                
        except Exception as e:
            messages.error(request, f"Error creating ETD form: {str(e)}")
            print(f"Error in create_etd_form_view: {str(e)}")
        
        return redirect('approval_requests')
    
    return redirect('approval_requests')
@login_required
def submit_request_view(request):
    if request.method == 'POST':
        email_alias = request.POST.get('email_alias')
        comments = request.POST.get('comments')
        
        try:
            # Create a new approval request
            approval_request = ApprovalRequest.objects.create(
                requester=request.user,
                email_alias=email_alias,
                comments=comments,
                status='pending'  # Set to pending when submitted
            )
            
            # Find approvers (users with admin or moderator roles)
            approvers = UserProfile.objects.filter(
                role__in=['admin', 'moderator'],
                is_active=True
            )
            
            # Create approval steps for each approver
            for approver in approvers:
                ApprovalStep.objects.create(
                    request=approval_request,
                    approver=approver
                )
            
            messages.success(request, "Your request has been submitted and is pending approval.")
        except Exception as e:
            # Fall back to the original behavior if models aren't set up yet
            messages.success(request, f"Your request has been submitted successfully! {str(e)}")
        
        return redirect('approval_requests')
    
    # If not POST request, redirect to approval requests page
    return redirect('approval_requests')

@login_required
def approve_request_view(request, step_id):
    """View for approving a request"""
    # Get the approval step that belongs to this approver
    step = get_object_or_404(ApprovalStep, id=step_id, approver=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        comment = request.POST.get('comment', '')
        
        if action == 'approve':
            # Mark this approval step as approved
            step.status = 'approved'
            step.comments = comment
            step.save()
            
            # Check if all steps are approved
            all_steps = ApprovalStep.objects.filter(request=step.request)
            all_approved = all(s.status == 'approved' for s in all_steps)
            
            if all_approved:
                # If all approvers have approved, update the main request status
                step.request.status = 'approved'
                step.request.save()
                # Here you would trigger PDF generation with LaTeX
                
            messages.success(request, "Request approved successfully.")
        
        elif action == 'return':
            # Mark this step as returned
            step.status = 'returned'
            step.comments = comment
            step.save()
            
            # Update the main request status to returned
            step.request.status = 'returned'
            step.request.save()
            
            messages.success(request, "Request returned for revisions.")
        
        return redirect('approval_requests')
    
    # If not a POST request, show the approval form
    return render(request, 'approve_request.html', {'step': step})

@login_required
def request_detail_view(request, request_id):
    """View for seeing details of a specific request"""
    approval_request = get_object_or_404(ApprovalRequest, id=request_id)
    
    # Security check: user should only see their own requests or requests they need to approve
    is_requester = approval_request.requester == request.user
    is_approver = ApprovalStep.objects.filter(request=approval_request, approver=request.user).exists()
    
    if not (is_requester or is_approver or request.user.role == 'admin'):
        messages.error(request, "You don't have permission to view this request.")
        return redirect('approval_requests')
    
    # Get all approval steps for this request
    steps = ApprovalStep.objects.filter(request=approval_request)
    
    context = {
        'request': approval_request,
        'steps': steps,
        'is_requester': is_requester,
        'is_approver': is_approver
    }
    
    return render(request, 'request_detail.html', context)

@login_required
def revise_request_view(request, request_id):
    """View for revising a returned request"""
    approval_request = get_object_or_404(ApprovalRequest, id=request_id, requester=request.user, status='returned')
    
    if request.method == 'POST':
        email_alias = request.POST.get('email_alias')
        comments = request.POST.get('comments')
        
        # Update the request
        approval_request.email_alias = email_alias
        approval_request.comments = comments
        approval_request.status = 'pending'  # Reset to pending
        approval_request.save()
        
        # Reset all approval steps to pending
        ApprovalStep.objects.filter(request=approval_request).update(status='pending', comments='')
        
        messages.success(request, "Your request has been revised and resubmitted.")
        return redirect('approval_requests')
    
    return render(request, 'revise_request.html', {'request': approval_request})


@login_required
def upload_signature(request):
    if request.method == "POST" and request.FILES.get("signature"):
        user_profile = request.user  # Since UserProfile extends AbstractUser, request.user is a UserProfile
        user_profile.signature = request.FILES["signature"]
        user_profile.save()

        messages.success(request, "Your signature has been uploaded successfully!")
        return redirect("approval_requests")  # Redirect back to the approval requests page

    return render(request, "approval_requests.html")


@login_required
def delete_signature(request):
    if request.method == 'POST':
        user = request.user

        # Check if the user has a signature image
        if user.signature:
            # Get the path to the file in the media folder
            signature_path = user.signature.path

            # Delete the image file from the filesystem
            if os.path.isfile(signature_path):
                os.remove(signature_path)

            # Clear the signature field in the user model
            user.signature = None
            user.save()


    return redirect('approval_requests')  # Redirect to profile page (or wherever appropriate)
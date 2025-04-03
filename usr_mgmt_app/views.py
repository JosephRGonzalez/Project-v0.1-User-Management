import os
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
from django.utils.timezone import now
import subprocess
from django.conf import settings
from .models import ThesisRequest, WithdrawalRequest
from django.http import FileResponse
from django.conf import settings





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
    thesis_requests = ThesisRequest.objects.filter(user=request.user).order_by('-created_at')[:5]  # Get last 5 requests
    withdrawal_requests = WithdrawalRequest.objects.filter(user=request.user).order_by('-created_at')[:5]

    # Render the dashboard template with the counts
    return render(request, 'dashboard.html', {
        'admin_count': admin_count,
        'moderator_count': moderator_count,
        'user_count': user_count,
        'thesis_requests': thesis_requests,
        'withdrawal_requests': withdrawal_requests,
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

#Dashboard Admin/User Count Cards
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


#Users List in user_list.html
@login_required
@permission_required('usr_mgmt_app.can_read', raise_exception=True)
def user_list(request):
    users = UserProfile.objects.all()

    pending_requests = []
    for request_obj in ThesisRequest.objects.filter(status="pending"):
        pending_requests.append({"request": request_obj, "type": "Thesis Request"})
    for request_obj in WithdrawalRequest.objects.filter(status="pending"):
        pending_requests.append({"request": request_obj, "type": "Withdrawal Request"})

    # Get the permissions for the current user
    has_edit_permission = request.user.has_perm('usr_mgmt_app.can_edit')
    has_manage_users_permission = request.user.has_perm('usr_mgmt_app.can_manage_users')

    # Add permissions to context
    context = {
        'has_edit_permission': has_edit_permission,
        'has_manage_users_permission': has_manage_users_permission,
        'users': UserProfile.objects.all(),  # Assuming you have users in your context
        'pending_requests': pending_requests,
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




#Signature Image Upload for Forms
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







LATEX_DIR = os.path.join(settings.BASE_DIR, "latex_templates/")
OUTPUT_DIR = os.path.join(settings.MEDIA_ROOT, "generated_pdfs/")

def generate_pdf_from_latex(user_data, template_file, output_filename):
    """Replace placeholders in LaTeX and compile using Makefile."""

    template_path = os.path.join(LATEX_DIR, template_file)
    output_tex_path = os.path.join(LATEX_DIR, output_filename + ".tex")

    print(f"Generating LaTeX file at: {output_tex_path}")

    with open(template_path, "r") as file:
        latex_content = file.read()

    for key, value in user_data.items():
        if value is None:
            value = ""  # Prevent None values from causing errors
        print(f"Replacing {key} with {value}")  # Debugging
        latex_content = latex_content.replace(f"{{{{{key}}}}}", str(value))

    print("\n🔍 FINAL LaTeX CONTENT AFTER REPLACEMENT:\n")
    print(latex_content)  # Debugging

    with open(output_tex_path, "w") as file:
        file.write(latex_content)

    if not os.path.exists(output_tex_path):
        raise FileNotFoundError(f"Error: LaTeX file {output_tex_path} was not created!")

    try:
        print(f"Running Makefile in: {LATEX_DIR}")
        result = subprocess.run(["make", "-C", LATEX_DIR], capture_output=True, text=True, check=True)
        print("Makefile output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("LaTeX Error:", e.stderr)
        raise

    pdf_path = os.path.join(OUTPUT_DIR, output_filename + ".pdf")
    print(f"✅ PDF should be generated at: {pdf_path}")
    return pdf_path





def fill_thesis_form(request):
    """Handles form submission for Thesis Request."""
    user = request.user



    # Check if a ThesisRequest already exists for the user
    existing_request = ThesisRequest.objects.filter(user=user).first()

    if request.method == "POST":
        print("Form submitted!")  # Debugging: Check if this prints in the terminal

        student_id = request.POST.get("student_id")
        degree_type = request.POST.get("degree_type")
        graduation_date = request.POST.get("graduation_date")
        request_type = request.POST.get("request_type")
        justification = request.POST.get("justification")


        if not all([student_id, degree_type, graduation_date, request_type, justification]):
            print("Missing form fields!")  # Debugging
            return render(request, "forms/thesis_form.html", {"error": "All fields are required."})

        # If a request already exists, update it
        if existing_request:
            existing_request.student_id = student_id
            existing_request.degree_type = degree_type
            existing_request.graduation_date = graduation_date
            existing_request.request_type = request_type
            existing_request.justification = justification
            existing_request.status = "Draft"
            existing_request.save()  # Save the updated data

        else:
            # If no existing request, create a new one
            ThesisRequest.objects.create(
                user=user,
                student_id=student_id,
                degree_type=degree_type,
                graduation_date=graduation_date,
                request_type=request_type,
                justification=justification,
                status = "Draft"
            )

        print("Thesis request saved:", existing_request.id if existing_request else "New")  # Debugging
        return redirect("fill_thesis_form")

    # Retrieve the latest request for the user (either existing or the last one created)
    thesis_request = existing_request or ThesisRequest.objects.filter(user=user).last()
    return render(
        request,
        "forms/thesis_form.html",
        {
                 "thesis_request": thesis_request,
                 "MEDIA_URL": settings.MEDIA_URL
                }
             )



def generate_thesis_pdf(request, request_id):
    """Generates a PDF for a Thesis Request."""
    thesis = ThesisRequest.objects.get(id=request_id)

    # Ensure SIGNATURE_FILENAME is correctly formatted
    if thesis.user.signature:
        signature_filename = os.path.join("../", thesis.user.signature.name)
    else:
        signature_filename = "../signatures/placeholder.png"

    user_data = {
        "FIRST_NAME": thesis.user.first_name,
        "LAST_NAME": thesis.user.last_name,
        "STUDENT_ID": thesis.student_id,
        "DEGREE_TYPE": thesis.degree_type,
        "GRADUATION_DATE": thesis.graduation_date,
        "REQUEST_TYPE": thesis.request_type,
        "JUSTIFICATION": thesis.justification,
        "SIGNATURE_FILENAME": signature_filename,
        "CREATED_AT": thesis.created_at,
    }

    print("User Data Sent to LaTeX:", user_data)  # Debugging

    # Generate the PDF from LaTeX template
    pdf_filename = f"thesis_filled_{request_id}.pdf"
    pdf_path = generate_pdf_from_latex(user_data, "thesis_template.tex", f"thesis_filled_{request_id}")

    # Store the PDF path in the model (relative to MEDIA_URL)
    thesis.pdf_document = os.path.join('generated_pdfs', pdf_filename)  # This is relative to MEDIA_URL
    thesis.status = "Draft"
    thesis.save()

    return FileResponse(open(pdf_path, "rb"), content_type="application/pdf")

@login_required
def submit_thesis_for_approval(request, request_id):
    thesis_request = get_object_or_404(ThesisRequest, id=request_id, user=request.user)

    if request.method == "POST":
        thesis_request.status = "Pending"  # Update status to Pending
        thesis_request.save()
        return redirect("fill_thesis_form")  # Redirect back to the form page

    return redirect("fill_thesis_form")





#######################
### Withdrawal Form ###
#######################
def fill_withdrawal_form(request):
    """Handles form submission for Withdrawal Request."""
    user = request.user

    # Check if a WithdrawalRequest already exists for the user
    existing_request = WithdrawalRequest.objects.filter(user=user).first()

    if request.method == "POST":
        # If a request already exists, update it
        if existing_request:
            existing_request.student_id = request.POST["student_id"]
            existing_request.college = request.POST["college"]
            existing_request.degree_plan = request.POST["degree_plan"]
            existing_request.street_address = request.POST["street_address"]
            existing_request.city = request.POST["city"]
            existing_request.state = request.POST["state"]
            existing_request.zipcode = request.POST["zipcode"]
            existing_request.middle_name = request.POST.get("middle_name", "")
            existing_request.email = request.POST["email"]
            existing_request.phone = request.POST["phone"]
            existing_request.withdrawal_term = request.POST["withdrawal_term"]
            existing_request.last_attendance_date = request.POST["last_attendance_date"]
            existing_request.withdrawal_reason = request.POST["withdrawal_reason"]
            existing_request.financial_assistance = request.POST.get("financial_assistance", False)
            existing_request.uh_health_insurance = request.POST.get("uh_health_insurance", False)
            existing_request.campus_housing = request.POST.get("campus_housing", False)
            existing_request.visa_holder = request.POST.get("visa_holder", False)
            existing_request.gi_bill = request.POST.get("gi_bill", False)
            existing_request.student_initial = user.first_name[0]  # Extract first initial
            existing_request.status = "Draft"
            existing_request.save()  # Save the updated data
        else:
            # If no existing request, create a new one
            WithdrawalRequest.objects.create(
                user=user,
                student_id=request.POST["student_id"],
                college=request.POST["college"],
                degree_plan=request.POST["degree_plan"],
                street_address=request.POST["street_address"],
                city=request.POST["city"],
                state=request.POST["state"],
                zipcode=request.POST["zipcode"],
                middle_name=request.POST.get("middle_name", ""),
                email=request.POST["email"],
                phone=request.POST["phone"],
                withdrawal_term=request.POST["withdrawal_term"],
                last_attendance_date=request.POST["last_attendance_date"],
                withdrawal_reason=request.POST["withdrawal_reason"],
                financial_assistance=request.POST.get("financial_assistance", False),
                uh_health_insurance=request.POST.get("uh_health_insurance", False),
                campus_housing=request.POST.get("campus_housing", False),
                visa_holder=request.POST.get("visa_holder", False),
                gi_bill=request.POST.get("gi_bill", False),
                student_initial=user.first_name[0],  # Extract first initial
                status = "Draft"
            )

        return redirect("fill_withdrawal_form")

    # Retrieve the latest request for the user (either existing or the last one created)
    withdrawal_request = existing_request or WithdrawalRequest.objects.filter(user=user).last()
    return render(
        request,
        "forms/withdrawal_form.html",
        {
            "withdrawal_request": withdrawal_request,
            "MEDIA_URL": settings.MEDIA_URL
        }
    )


def generate_withdrawal_pdf(request, request_id):
    """Generates a PDF for a Withdrawal Request."""
    withdrawal = WithdrawalRequest.objects.get(id=request_id)

    # Ensure SIGNATURE_FILENAME points to the correct file
    if withdrawal.user.signature:
        signature_filename = os.path.join("../", withdrawal.user.signature.name)
    else:
        signature_filename = "../signatures/placeholder.png"

    user_data = {
        "FIRST_NAME": withdrawal.user.first_name,
        "MIDDLE_NAME": withdrawal.middle_name if withdrawal.middle_name else "",
        "LAST_NAME": withdrawal.user.last_name,
        "EMAIL": withdrawal.email,
        "STUDENT_ID": withdrawal.student_id,
        "COLLEGE": withdrawal.college,
        "DEGREE_PLAN": withdrawal.degree_plan,
        "STREET_ADDRESS": withdrawal.street_address,
        "CITY": withdrawal.city,
        "STATE": withdrawal.state,
        "ZIPCODE": withdrawal.zipcode,
        "PHONE": withdrawal.phone,
        "WITHDRAWAL_TERM": withdrawal.withdrawal_term,
        "LAST_ATTENDANCE_DATE": withdrawal.last_attendance_date,
        "WITHDRAWAL_REASON": withdrawal.withdrawal_reason,
        "FINANCIAL_ASSISTANCE": "Yes" if withdrawal.financial_assistance else "No",
        "UH_HEALTH_INSURANCE": "Yes" if withdrawal.uh_health_insurance else "No",
        "CAMPUS_HOUSING": "Yes" if withdrawal.campus_housing else "No",
        "VISA_HOLDER": "Yes" if withdrawal.visa_holder else "No",
        "GI_BILL": "Yes" if withdrawal.gi_bill else "No",
        "STUDENT_INITIAL": withdrawal.user.first_name[0],
        "SIGNATURE_FILENAME": signature_filename,
        "CREATED_AT": withdrawal.created_at,
    }

    print("User Data Sent to LaTeX:", user_data)  # Debugging

    # Generate the PDF from LaTeX template
    pdf_filename = f"withdrawal_filled_{request_id}.pdf"
    pdf_path = generate_pdf_from_latex(user_data, "withdrawal_template.tex", f"withdrawal_filled_{request_id}")

    # Store the PDF path in the model (relative to MEDIA_URL)
    withdrawal.pdf_document = os.path.join('generated_pdfs', pdf_filename)  # This is relative to MEDIA_URL
    withdrawal.status = "Draft"
    withdrawal.save()

    return FileResponse(open(pdf_path, "rb"), content_type="application/pdf")


@login_required
def submit_withdrawal_for_approval(request, request_id):
    withdrawal_request = get_object_or_404(WithdrawalRequest, id=request_id, user=request.user)

    if request.method == "POST":
        withdrawal_request.status = "Pending"  # Update status to Pending
        withdrawal_request.save()
        return redirect("fill_withdrawal_form")  # Redirect back to the form page

    return redirect("fill_withdrawal_form")






# Used for tracking user forms.
def approval_requests(request):
    print("Current User:", request.user)
    print("Is Authenticated?", request.user.is_authenticated)

    user_thesis_requests = ThesisRequest.objects.filter(user=request.user)
    user_withdrawal_requests = WithdrawalRequest.objects.filter(user=request.user)

    print("Thesis Requests:", list(user_thesis_requests))
    print("Withdrawal Requests:", list(user_withdrawal_requests))

    return render(request, "approval_requests.html", {
        "thesis_requests": user_thesis_requests,
        "withdrawal_requests": user_withdrawal_requests,
    })


def approve_request(request, request_id):
    form_request = get_object_or_404(ApprovalRequest, id=request_id)
    if request.user.role == "admin":
        form_request.status = "approved"
        form_request.save()
    return redirect('user_list')

def return_request(request, request_id):
    form_request = get_object_or_404(ApprovalRequest, id=request_id)
    if request.user.role == "admin":
        form_request.status = "returned"
        form_request.save()
    return redirect('user_list')


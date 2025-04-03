import os
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError



# Validation for Signature Image Upload
def validate_signature_file(value):
    ext = os.path.splitext(value.name)[1]  # Get file extension
    valid_extensions = ['.png', '.jpg', '.jpeg']
    if ext.lower() not in valid_extensions:
        raise ValidationError('Unsupported file format. Allowed formats: PNG, JPG, JPEG.')



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
    signature = models.ImageField(upload_to='signatures/', null=True, blank=True, validators=[validate_signature_file])
    groups = models.ManyToManyField(Group, related_name="userprofile_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="userprofile_permissions", blank=True)
    
    class Meta:
        permissions = [
            ("can_read", "Can read data"),
            ("can_edit", "Can edit data"),
            ("can_manage_users", "Can activate/deactivate and delete users"),
            ("can_approve", "Can approve requests"),  # Added new permission
        ]
    
    def __str__(self):
        return f"{self.username} ({self.role})"








class ApprovalRequest(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('returned', 'Returned'),
        ('approved', 'Approved'),
    )
    
    requester = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='requests')
    email_alias = models.CharField(max_length=100)
    comments = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    pdf_document = models.FileField(upload_to='generated_pdfs/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Request #{self.id} by {self.requester.username} - {self.status}"

class ApprovalStep(models.Model):
    request = models.ForeignKey(ApprovalRequest, on_delete=models.CASCADE, related_name='steps')
    approver = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='approval_steps')
    status = models.CharField(max_length=20, choices=ApprovalRequest.STATUS_CHOICES, default='pending')
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Approval step for Request #{self.request.id} by {self.approver.username}"

class ETDForm(models.Model):
    REQUEST_CHOICES = (
        ('first_extension', 'First Embargo Extension'),
        ('additional_extension', 'Additional Embargo Extension'),
        ('full_hold', 'Full Record Hold'),
        ('other', 'Other')
    )
    
    DEGREE_CHOICES = (
        ('masters', 'Master'),
        ('doctorate', 'Doctorate')
    )
    
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='etd_forms')
    student_id_number = models.CharField(max_length=100)
    degree_type = models.CharField(max_length=20, choices=DEGREE_CHOICES)
    graduation_date = models.CharField(max_length=50)
    request_type = models.CharField(max_length=20, choices=REQUEST_CHOICES)
    justification = models.TextField()
    pdf_document = models.FileField(upload_to='generated_forms/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=ApprovalRequest.STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ETD Form for {self.student.username} - {self.get_request_type_display()}"









from django.db import models
from django.contrib.auth import get_user_model

UserProfile = get_user_model()  # Ensure it references the correct User model

class ThesisRequest(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('returned', 'Returned'),
        ('approved', 'Approved'),
    ]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="thesis_requests")
    student_id = models.CharField(max_length=7, default="0000000")  # Default 7-digit placeholder
    degree_type = models.CharField(
        max_length=20,
        choices=[("Master", "Master"), ("Doctorate", "Doctorate")],
        default="Master"
    )
    graduation_date = models.CharField(max_length=10, default="MM/YYYY")  # Default format
    request_type = models.CharField(max_length=50, default="Unknown Request")
    justification = models.TextField(default="No justification provided")  # Default text
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    pdf_document = models.FileField(upload_to="generated_pdfs/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Thesis Request {self.id} by {self.user.username} - {self.status}"


class WithdrawalRequest(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('returned', 'Returned'),
        ('approved', 'Approved'),
    ]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="withdrawal_requests")
    student_id = models.CharField(max_length=7, default="0000000")
    middle_name = models.CharField(max_length=50, blank=True, null=True)  # New field for middle name
    email = models.EmailField(default="example@example.com")  # New field for email
    college = models.CharField(max_length=100, default="Unknown College")
    degree_plan = models.CharField(max_length=100, default="Unknown Degree Plan")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')

    street_address = models.CharField(max_length=255, default="No address provided")
    city = models.CharField(max_length=100, default="Unknown City")
    state = models.CharField(max_length=50, default="Unknown State")
    zipcode = models.CharField(max_length=10, default="00000")

    phone = models.CharField(max_length=15, default="000-000-0000")
    withdrawal_term = models.CharField(max_length=20, default="Spring 2025")
    last_attendance_date = models.DateField(null=True, blank=True)
    withdrawal_reason = models.TextField(default="No reason provided")
    financial_assistance = models.BooleanField(default=False)
    uh_health_insurance = models.BooleanField(default=False)
    campus_housing = models.BooleanField(default=False)
    visa_holder = models.BooleanField(default=False)
    gi_bill = models.BooleanField(default=False)
    student_initial = models.CharField(max_length=1, default="-")
    pdf_document = models.FileField(upload_to="generated_pdfs/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Withdrawal Request {self.id} by {self.user.username} - {self.status}"

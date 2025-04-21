import os
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator



# Validation for Signature Image Upload
def validate_signature_file(value):
    ext = os.path.splitext(value.name)[1]  # Get file extension
    valid_extensions = ['.png', '.jpg', '.jpeg']
    if ext.lower() not in valid_extensions:
        raise ValidationError('Unsupported file format. Allowed formats: PNG, JPG, JPEG.')




class Unit(models.Model):
    name = models.CharField(max_length=255)  # e.g., "Computer Science"
    code = models.SlugField(unique=True)     # e.g., "cs", "nsm"
    is_college = models.BooleanField(default=False)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='sub_units',
        on_delete=models.CASCADE
    )

    def __str__(self):
        if self.is_college:
            return f"{self.name} (College)"
        elif self.parent:
            return f"{self.name} - {self.parent.name}"
        return self.name



class UserProfile(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('user', 'User'),
    ]

    ACADEMIC_LEVEL_CHOICES = [
        ('undergraduate', 'Undergraduate'),
        ('graduate', 'Graduate'),
    ]


    cougar_id = models.CharField(max_length=7,unique=True,null=True,blank=True,validators=[RegexValidator(regex=r'^\d{7}$', message='Cougar ID must be exactly 7 digits')])
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    academic_level = models.CharField(max_length=15, choices=ACADEMIC_LEVEL_CHOICES, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    profile_banner = models.ImageField(upload_to='banner_pictures/', null=True,blank=True)
    bio = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    signature = models.ImageField(upload_to='signatures/', null=True, blank=True, validators=[validate_signature_file])
    groups = models.ManyToManyField(Group, related_name="userprofile_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="userprofile_permissions", blank=True)
    unit = models.ForeignKey(Unit, null=True, blank=True, on_delete=models.SET_NULL)
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





class ReducedCourseLoadRequest(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('returned', 'Returned'),
        ('approved', 'Approved'),
    ]

    SEMESTER_CHOICES = [
        ('fall', 'Fall'),
        ('spring', 'Spring'),
    ]

    MAIN_REASON_CHOICES = [
        ('academic', 'Academic Difficulty'),
        ('medical', 'Medical Reason'),
        ('final', 'Final Semester'),
    ]

    ACADEMIC_TYPE_CHOICES = [
        ('IAI', 'Initial Adjustment Issues'),
        ('ICLP', 'Improper Course Level Placement'),
    ]

    IAI_REASONS = [
        ('english_language', 'English Language'),
        ('reading_requirements', 'Reading Requirements'),
        ('american_teaching', 'Unfamiliarity with American Teaching Methods'),
    ]

    FINAL_TYPE_CHOICES = [
        ('non_thesis', 'Non-Thesis Track'),
        ('thesis', 'Thesis/Dissertation Track'),
    ]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="rcl_requests")
    student_id = models.CharField(max_length=7)

    # Primary reason
    reason = models.CharField(max_length=10, choices=MAIN_REASON_CHOICES)

    # Academic option details
    academic_type = models.CharField(max_length=10, choices=ACADEMIC_TYPE_CHOICES, blank=True, null=True)
    iai_reasons = models.JSONField(blank=True, null=True)

    # Medical
    medical_letter_attached = models.BooleanField(default=False)

    # Final semester
    final_type = models.CharField(max_length=20, choices=FINAL_TYPE_CHOICES, blank=True, null=True)
    final_semester_hours = models.PositiveIntegerField(blank=True, null=True)
    thesis_hours = models.PositiveIntegerField(blank=True, null=True)

  # Common fields
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    semester_year = models.PositiveIntegerField(default=25)
    # Courses to Drop
    course_to_drop_1 = models.CharField(max_length=20, default="")  # Required
    course_to_drop_2 = models.CharField(max_length=20, blank=True, default="")  # Optional
    course_to_drop_3 = models.CharField(max_length=20, blank=True, default="")  # Optional

    total_credit_hours_after_drop = models.PositiveIntegerField()
    current_semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES, default = 'fall')
    current_year = models.PositiveIntegerField(default=25)

    pdf_document = models.FileField(upload_to="generated_pdfs/", null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RCL Request {self.id} by {self.user.username} - {self.status}"




class PetitionRequest(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Pending', 'Pending Review'),
        ('Returned', 'Returned for Revision'),
        ('Approved', 'Approved'),
    ]
    
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="petition_requests")
    student_id = models.CharField(max_length=7, default="0000000")
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(default="example@example.com")
    phone = models.CharField(max_length=15, default="000-000-0000")
    
    # Current Student Information
    career = models.CharField(max_length=20, default="GRAD")  # GRAD, PRFL
    program = models.CharField(max_length=20, default="Unknown Program")  # PhD, MA, MS, etc.
    plan_code = models.CharField(max_length=20, default="Unknown Plan")
    
    # Petition Effective
    term = models.CharField(max_length=10, default="Fall")  # Fall, Spring, Summer
    year = models.CharField(max_length=4, default="2025")
    
    # Purpose of Petition (1-10)
    purpose = models.CharField(max_length=2, default="10")
    other_purpose = models.CharField(max_length=200, blank=True, null=True)
    
    # Transfer Credit Info (only used if purpose=9)
    institution_name = models.CharField(max_length=100, blank=True, null=True)
    city_state_zip = models.CharField(max_length=100, blank=True, null=True)
    transfer_start_term = models.CharField(max_length=10, blank=True, null=True)
    transfer_start_year = models.CharField(max_length=4, blank=True, null=True)
    transfer_end_term = models.CharField(max_length=10, blank=True, null=True)
    transfer_end_year = models.CharField(max_length=4, blank=True, null=True)
    credit_description = models.TextField(blank=True, null=True)
    hours_transferred = models.CharField(max_length=5, blank=True, null=True)
    requested_hours = models.CharField(max_length=5, blank=True, null=True)
    
    # Explanation
    explanation = models.TextField(default="No explanation provided")
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    pdf_document = models.FileField(upload_to='generated_pdfs/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Petition Request {self.id} by {self.user.username} - {self.status}"
    
    def get_status_display(self):
        return dict(self.STATUS_CHOICES)[self.status]





import os
import subprocess
import tempfile
from django.conf import settings
from django.template.loader import render_to_string
from .models import ApprovalRequest, ApprovalStep

def generate_approval_pdf(request_id):
    """
    Generate a PDF for an approved request using LaTeX
    """
    try:
        # Get the request and its steps
        approval_request = ApprovalRequest.objects.get(id=request_id)
        steps = ApprovalStep.objects.filter(request=approval_request)
        
        # Only generate PDF for approved requests
        if approval_request.status != 'approved':
            return None
        
        # Create a temporary directory for our LaTeX files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Prepare data for the template
            context = {
                'request_id': approval_request.id,
                'requester_name': f"{approval_request.requester.first_name} {approval_request.requester.last_name}",
                'email_alias': approval_request.email_alias,
                'submission_date': approval_request.created_at.strftime('%B %d, %Y'),
                'status': approval_request.get_status_display(),
                'comments': approval_request.comments,
                'approvals_table': _format_approvals_for_latex(steps),
                'signature_path': _get_signature_path(approval_request.requester),
                'approver_signature_path': _get_final_approver_signature(steps),
            }
            
            # Create LaTeX file from template
            template_path = os.path.join(settings.BASE_DIR, 'templates', 'latex', 'approval_form.tex')
            with open(template_path, 'r') as template_file:
                template_content = template_file.read()
            
            # Replace placeholders
            for key, value in context.items():
                template_content = template_content.replace('{{' + key + '}}', str(value))
            
            # Write the filled template to a temporary file
            temp_tex_path = os.path.join(temp_dir, f"approval_{request_id}.tex")
            with open(temp_tex_path, 'w') as output_file:
                output_file.write(template_content)
            
            # Create the output directory if it doesn't exist
            output_dir = os.path.join(settings.MEDIA_ROOT, 'generated_pdfs')
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate PDF using pdflatex
            output_pdf = os.path.join(output_dir, f"approval_{request_id}.pdf")
            subprocess.run(['pdflatex', '-output-directory', temp_dir, temp_tex_path], 
                          check=True, stdout=subprocess.PIPE)
            
            # Move the generated PDF to the final location
            temp_pdf_path = os.path.join(temp_dir, f"approval_{request_id}.pdf")
            if os.path.exists(temp_pdf_path):
                with open(temp_pdf_path, 'rb') as src_file:
                    with open(output_pdf, 'wb') as dest_file:
                        dest_file.write(src_file.read())
            
            # Return the relative path to the generated PDF
            return os.path.join('generated_pdfs', f"approval_{request_id}.pdf")
    
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return None

def _format_approvals_for_latex(steps):
    """Format approval steps for the LaTeX table"""
    result = ""
    for step in steps:
        approver_name = f"{step.approver.first_name} {step.approver.last_name}"
        status = step.get_status_display()
        date = step.updated_at.strftime('%B %d, %Y') if step.status == 'approved' else "-"
        result += f"{approver_name} & {status} & {date} \\\\\n    "
    return result

def _get_signature_path(user):
    """Get the signature image path for a user"""
    # This assumes you have a UserProfile with a signature field
    # If you don't have this yet, return a placeholder
    try:
        if hasattr(user, 'signature') and user.signature:
            return str(user.signature.path)
    except:
        pass
    return "signature_placeholder.png"  # Path to a placeholder signature image

def _get_final_approver_signature(steps):
    """Get the signature of the final approver"""
    # Find the last approver who approved the request
    for step in reversed(list(steps)):
        if step.status == 'approved':
            return _get_signature_path(step.approver)
    return "signature_placeholder.png"  # Path to a placeholder signature image
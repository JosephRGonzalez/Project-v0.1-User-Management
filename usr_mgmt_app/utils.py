import os
import subprocess
import tempfile
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
from .models import ApprovalRequest, ApprovalStep, UserProfile, ETDForm

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

def generate_etd_form(student_id, form_data):
    """
    Generate a PDF for an ETD Special Circumstance Form
    
    Args:
        student_id: The student's ID number
        form_data: Dictionary containing form fields
    
    Returns:
        String path to the generated PDF, or None if generation failed
    """
    try:
        # Get student information
        student = UserProfile.objects.get(id=student_id)
        
        # Create a temporary directory for our LaTeX files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Prepare data for the template
            context = {
                'student_name': f"{student.first_name} {student.last_name}",
                'student_id': form_data.get('student_id', ''),
                'degree_type': form_data.get('degree_type', ''),
                'graduation_date': form_data.get('graduation_date', ''),
                'justification': form_data.get('justification', ''),
                'student_signature': _get_signature_path(student),
                'student_signature_date': datetime.now().strftime('%B %d, %Y')
            }
            
            # Create the LaTeX template directory if it doesn't exist
            template_dir = os.path.join(settings.BASE_DIR, 'templates', 'latex')
            os.makedirs(template_dir, exist_ok=True)
            
            # Create a basic LaTeX template if it doesn't exist
            template_path = os.path.join(template_dir, 'etd_form.tex')
            if not os.path.exists(template_path):
                with open(template_path, 'w') as f:
                    f.write(r'''\documentclass[12pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{graphicx}
\usepackage{geometry}
\usepackage{datetime}

\geometry{a4paper, margin=1in}
\pagestyle{plain}

\begin{document}

\begin{center}
    \Large\textbf{ELECTRONIC THESIS/DISSERTATION SPECIAL CIRCUMSTANCE FORM}
\end{center}

\bigskip

\noindent\textbf{Student's Name:} {{student_name}} \hfill \textbf{Student ID number:} {{student_id}}

\bigskip

\noindent\textbf{Degree:} {{degree_type}} \hfill \textbf{Date of Graduation (Month Year):} {{graduation_date}}

\bigskip

\noindent\fbox{\begin{minipage}{\textwidth}
\textbf{SPECIAL REQUEST OPTIONS}

\smallskip

\begin{itemize}
  \item[$\square$] \textbf{First Embargo Extension}
  \item[$\square$] \textbf{Additional Embargo Extension}
  \item[$\square$] \textbf{Full Record Hold}
  \item[$\square$] \textbf{Other}
\end{itemize}

\end{minipage}}

\bigskip

\noindent\fbox{\begin{minipage}{\textwidth}
\textbf{Reasoning/justification for Special Request:}
\vspace{1cm}

{{justification}}

\smallskip

\end{minipage}}

\bigskip

\noindent\fbox{\begin{minipage}{\textwidth}
\textbf{STUDENT AGREEMENT}

\smallskip

I certify that the information provided above is correct and true.

\vspace{1cm}

\noindent\begin{tabular}{p{7cm}p{7cm}}
\includegraphics[width=5cm]{{"{{student_signature}}"}} & \\
\cline{1-1}
Student's Signature & Date: {{student_signature_date}}
\end{tabular}

\end{minipage}}

\end{document}''')
            
            # Read the template
            with open(template_path, 'r') as template_file:
                template_content = template_file.read()
            
            # Replace placeholders
            for key, value in context.items():
                template_content = template_content.replace('{{' + key + '}}', str(value))
            
            # Write the filled template to a temporary file
            temp_tex_path = os.path.join(temp_dir, f"etd_form_{student_id}.tex")
            with open(temp_tex_path, 'w') as output_file:
                output_file.write(template_content)
            
            # Create the output directory if it doesn't exist
            output_dir = os.path.join(settings.MEDIA_ROOT, 'generated_forms')
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate PDF using pdflatex
            output_pdf = os.path.join(output_dir, f"etd_form_{student_id}.pdf")
            try:
                subprocess.run(['pdflatex', '-output-directory', temp_dir, temp_tex_path], 
                            check=True, stdout=subprocess.PIPE)
                
                # Move the generated PDF to the final location
                temp_pdf_path = os.path.join(temp_dir, f"etd_form_{student_id}.pdf")
                if os.path.exists(temp_pdf_path):
                    with open(temp_pdf_path, 'rb') as src_file:
                        with open(output_pdf, 'wb') as dest_file:
                            dest_file.write(src_file.read())
                    
                    # Return the relative path to the generated PDF
                    return os.path.join('generated_forms', f"etd_form_{student_id}.pdf")
            except subprocess.CalledProcessError as e:
                print(f"Error running pdflatex: {str(e)}")
                # If pdflatex fails, create a simple text file instead
                with open(output_pdf, 'w') as f:
                    f.write(f"ETD Form for {student.first_name} {student.last_name}\n")
                    f.write(f"Student ID: {form_data.get('student_id', '')}\n")
                    f.write(f"Degree: {form_data.get('degree_type', '')}\n")
                    f.write(f"Graduation Date: {form_data.get('graduation_date', '')}\n")
                    f.write(f"Justification: {form_data.get('justification', '')}\n")
                
                return os.path.join('generated_forms', f"etd_form_{student_id}.pdf")
    
    except Exception as e:
        print(f"Error generating ETD form: {str(e)}")
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
            return user.signature.path
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
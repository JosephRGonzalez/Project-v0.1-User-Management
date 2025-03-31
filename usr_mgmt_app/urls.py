from django.urls import path
from . import views
from .views import upload_signature
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('', views.landing_page, name='landing_page'),  # Landing page
    path('login/', views.login_view, name='login'),  # Login page
    path('signup/', views.signup_view, name='signup'),  # Sign up Page
    path('dashboard/', views.dashboard_view, name='dashboard'),  # Dashboard page
    path('approval-requests/', views.approval_requests_view, name='approval_requests'),
    path('submit-request/', views.submit_request_view, name='submit_request'),  # Submit approval request
    path('approve-request/<int:step_id>/', views.approve_request_view, name='approve_request'),  # Approve/return request
    path('request/<int:request_id>/', views.request_detail_view, name='request_detail'),  # View request details
    path('revise-request/<int:request_id>/', views.revise_request_view, name='revise_request'),  # Revise returned request
    path('logout/', views.logout_view, name='logout'),
    path('users/', views.user_list, name='user_list'),  # List of users
    path('user/create/', views.user_create, name='user_create'),  # Add new user
    path('user/<int:user_id>/edit/', views.user_edit, name='user_edit'),  # Edit user
    path('user/<int:id>/deactivate/', views.user_deactivate, name='user_deactivate'),  # Deactivate user
    path('user/<int:id>/delete/', views.user_delete, name='user_delete'),  # Delete user
    path('user/<int:user_id>/toggle-status/', views.user_toggle_status, name='user_toggle_status'),  # Activate/Deactivate toggle
    path("upload-signature/", upload_signature, name="upload_signature"),  #Signature Upload
    path('delete_signature/', views.delete_signature, name='delete_signature'), #Delete Signature
    # Forms
    path("fill-form/thesis/", views.fill_thesis_form, name="fill_thesis_form"),
    path("fill-form/withdrawal/", views.fill_withdrawal_form, name="fill_withdrawal_form"),
    # PDF Generation
    path("generate-pdf/thesis/<int:request_id>/", views.generate_thesis_pdf, name="generate_thesis_pdf"),
    path("generate-pdf/withdrawal/<int:request_id>/", views.generate_withdrawal_pdf, name="generate_withdrawal_pdf"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
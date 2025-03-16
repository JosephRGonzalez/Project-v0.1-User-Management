from django.urls import path
from . import views
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
]
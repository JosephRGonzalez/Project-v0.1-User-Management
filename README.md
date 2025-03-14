# Thunder Bay: User Management System

### Team Members:
- **Haitham Yousif**
- **David Eldridge**
- **Joseph Gonzalez**
- **Andres Elias Meraz**

---

## Project Overview

Welcome to the **User Management System**, a robust web application designed to streamline the management of user profiles with a focus on security, flexibility, and user experience. Built with Django, this system enables organizations to easily manage user roles, permissions, and perform various CRUD (Create, Read, Update, Delete) operations, with an intuitive interface and role-based access control.

The system is designed to manage three distinct user roles:

- **Admin**: Full control over user management, including deactivation/reactivation, deletion, and editing.
- **Moderator**: Limited editing permissions, including the ability to read and modify user details.
- **User**: View-only permissions with no modification capabilities.

With features such as **user authentication** (via Microsoft Graph API for Azure AD), **role-based access control**, and **dynamic permissions**, this app empowers admins to efficiently manage users while maintaining a secure environment.

---

## Live Demo

Experience the User Management System live by visiting the [demo site](http://usr-mgmt-app-bue8bpeqcucthdc8.westus2-01.azurewebsites.net). The demo showcases all the core features of the app, including:

- **Login/Sign Up**: Secure access to the system.
- **Dashboard**: Admin and Moderator roles have customized access and functionalities.
- **User Management**: View and manage user profiles, roles, and statuses.
  
### **Demo Screenshots:**
- **Landing Page**:
  ![Landing Page](images/landing_page_screenshot.png)

- **Login Page**: 
  ![Login Page](images/login_screenshot.png)
  
- **Sign Up Page**: 
  ![Sign Up Page](images/signup_screenshot.png)

---

## Key Features

### 1. **Role-Based Access Control (RBAC)**
   - **Admins** can read, edit, delete, and deactivate/activate users. Full control over user management.
   - **Moderators** can view and edit user profiles, but cannot delete or deactivate users.
   - **Users** can only view their profile details and cannot make any modifications.

### 2. **User Profile Management**
   - Create and manage user profiles including name, email, and assigned role (Admin, Moderator, User).
   - Deactivate or reactivate user accounts for better user lifecycle management.

### 3. **Permissions**
   - Permissions are automatically assigned based on the user’s role. This ensures seamless, dynamic access control with minimal manual configuration.
   - A user can only access certain features depending on their role, reducing the risk of unauthorized actions.

### 4. **Secure Authentication**
   - Authentication via Microsoft Graph API allows for seamless login and signup using Microsoft Azure Active Directory (Azure AD).
   - Ensures secure login using OAuth, protecting sensitive data.

---

## Technologies Used

- **Frontend**: HTML, CSS (Bootstrap 5), JavaScript
- **Backend**: Django 4.2
- **Database**: SQLite (for development), scalable to other databases like PostgreSQL in production.
- **Authentication**: Microsoft Graph API (Azure AD integration)
- **Deployment**: Azure Web App

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


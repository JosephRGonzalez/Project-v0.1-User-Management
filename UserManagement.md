
# Thundery Bay: User Management System Documentation

## Overview

This project is a web-based user management system built using **Django** as the backend framework, **SQLite** as the database, and **Office 365 authentication** integrated via **Microsoft Graph API**. It allows for role-based access control (RBAC) with users, moderators, and admins, each having different levels of access. The application is hosted on **Azure** using **Azure Web Apps**, ensuring scalability and availability.

## Key Features

1. **Role-Based Access Control (RBAC)**:  
   The system defines three user roles:
   - **Users**: Read-only access to their profile and basic settings.
   - **Moderators**: Can read and edit user data, but with limited permissions.
   - **Admins**: Full access to manage users, including CRUD operations, and can activate/deactivate user accounts.

2. **Authentication with Office 365**:  
   Users authenticate using their Office 365 credentials, making the system easily integrable with organizations using Office 365. The authentication process is powered by **Microsoft Graph API**, allowing seamless integration with Azure Active Directory (Azure AD).

3. **Database**:  
   The system uses **SQLite** as the database to store user data and role assignments. Each user is associated with a specific role, and their data is stored securely within the database. SQLite was chosen for its simplicity and suitability for small to medium-sized applications.

4. **Frontend**:  
   The frontend is designed using **HTML**, **CSS**, and **JavaScript**. It provides a user-friendly interface with forms for user registration, login, and profile management. Dynamic content is rendered using Django templates, and frontend interactions are enhanced using JavaScript for improved user experience.

5. **Deployment on Azure**:  
   The system is hosted on **Azure Web Apps**, which provides a secure and scalable platform for deploying web applications. The deployment process is automated using **Azure DevOps** pipelines, ensuring that the latest changes are pushed to production without manual intervention.

## Technologies Used

- **Django**: Backend framework for building robust and scalable web applications.
- **SQLite**: Lightweight, serverless database for local development and small production applications.
- **Office 365 Authentication**: Integrated via Microsoft Graph API to authenticate users via Azure Active Directory.
- **HTML/CSS/JavaScript**: For the frontend, providing a responsive and interactive user interface.
- **Azure Web Apps**: Cloud hosting platform for deploying and managing web applications at scale.

### **Database Schema Overview**

The project uses **Django** and **SQLite** to manage user data and roles. The primary model in this schema is the `UserProfile`, which extends Django's built-in `AbstractUser` to add custom fields and functionalities for user authentication and role-based access control (RBAC).

#### **Models**

1. **UserProfile**:  
   The `UserProfile` model extends `AbstractUser`, which means it inherits the default user fields (like `username`, `email`, `password`, etc.) but also includes custom fields specific to the project.

   - **role**:  
     A `CharField` that defines the user's role within the system. The `role` field is a choice field with three possible values:
     - `'admin'`: Full access to all features, including user management.
     - `'moderator'`: Limited permissions for content management.
     - `'user'`: Basic access with read-only permissions.

   - **is_active**:  
     A `BooleanField` that tracks whether the user is active or not. Inactive users can be deactivated but not deleted, maintaining a record of their existence in the system.

   - **created_at**:  
     A `DateTimeField` that automatically records when the user was created.

   - **updated_at**:  
     A `DateTimeField` that automatically updates when the user record is modified.

   - **groups**:  
     A `ManyToManyField` that links the user to Django's `Group` model, allowing users to be assigned to different groups with associated permissions.

   - **user_permissions**:  
     Another `ManyToManyField` that links the user to Django's `Permission` model. This field allows for granular control over what actions users can perform.

   - **Meta class**:  
     The `Meta` class defines custom permissions for the `UserProfile` model:
     - `"can_read"`: Permission to read data.
     - `"can_edit"`: Permission to edit data.
     - `"can_manage_users"`: Permission to manage users (activate/deactivate, delete).

#### **Key Points of the Schema**:
- **User Authentication**:  
  The `UserProfile` inherits from `AbstractUser`, which means it integrates seamlessly with Django's built-in authentication system. This enables the use of standard authentication workflows (like login, logout, password reset, etc.).

- **Role-based Access Control (RBAC)**:  
  The `role` field allows for three distinct roles (`admin`, `moderator`, `user`), with different levels of access. Admin users have full control, while moderators and users have restricted access. This is a core feature of the system, and it's used to ensure that users have the right permissions based on their role.

- **Permissions**:  
  The model includes custom permissions that allow for detailed access control:
  - `can_read`: Users with this permission can read data in the system.
  - `can_edit`: Users with this permission can edit data.
  - `can_manage_users`: Admins can use this permission to manage the activation, deactivation, and deletion of users.

- **Groups and Permissions**:  
  The `groups` and `user_permissions` fields integrate with Django’s existing `Group` and `Permission` models. This allows for flexible permission management and easier organization of users.


## Office 365 Authentication

The authentication is handled by integrating with **Azure Active Directory** via **Microsoft Graph API**. Upon successful login, the system retrieves the user's profile from Azure AD, ensuring that only authorized users can access the system. This integration makes the application highly secure and seamless for users already within an Office 365 ecosystem.

## Deployment Process

1. **Push the code to Azure**:  
   The application is pushed to **Azure Web Apps** using **Git** or through a **CI/CD pipeline** (Azure DevOps). 
   
2. **Database setup**:  
   SQLite is used as the database for local storage, and migration commands are used to sync the database schema.

3. **Environment Configuration**:  
   The application is configured to work with **Azure Active Directory** for authentication. Necessary environment variables are set in the Azure portal, including API keys and database settings.

4. **Web Hosting**:  
   The app is accessible through the **Azure Web App URL**, which ensures that the system is available for users from anywhere, with automatic scaling handled by Azure.

## Conclusion

This **User Management System** provides a secure, efficient, and scalable solution for managing users with different access levels. By leveraging Django, SQLite, Office 365 authentication, and Azure's cloud platform, the application ensures a seamless user experience and is ready for deployment in any organizational setting.

--- 

This will give a comprehensive overview of what you've implemented! Let me know if you want any changes or additions.
# ProjectShala
ProjectShala is a comprehensive project management platform designed to streamline collaboration, enhance communication, and improve task management for organizations. It offers a user-friendly interface with powerful tools to manage projects, assign tasks, and monitor progress efficiently.

## Introduction
ProjectShala is built to address the common challenges in project management, such as inefficient collaboration, poor communication, and disorganized task management. It caters to different user roles, including Super-Admin, Admins, and Users, ensuring tailored access and functionality for each role.

## Features
- User Management: Manage users with role-based access control.
- Project Management: Create, manage, and track projects efficiently.
- Task Assignment: Assign and manage tasks with deadlines and priorities.
- Communication Tools: Integrated messaging, discussion boards, and file sharing.
- Calendar and Scheduling: Schedule events, set reminders, and sync with external calendars.
- Reporting and Analytics: Generate custom reports and view real-time analytics.
- Security: Robust security features, including data encryption and access control.

## Tech-Stack
- ReactJS
- Django
- MongoDB
- HTML
- Python

## Running The Program
- rm -rf .venv
- python3 -m venv .venv
- source .venv/bin/activate
- pip install -r requirements.txt
- rm -rf mysite/main/migrations
- find . -path "/migrations/.py" -not -name "_init_.py" -delete
- find . -path "/migrations/.pyc"  -delete
- rm db.sqlite3
- python3 manage.py makemigrations
- python3 manage.py migrate
- python manage.py migrate --run-syncdb
- python3 manage.py runserver

## Usage

### Super-Admin
- Create and manage Admin and User accounts.
- Configure platform-wide settings.
- Monitor projects and user activity.
### Admin
- Create and manage projects.
- Assign tasks to Users.
- Track project progress and generate reports.
### User
- View and manage assigned tasks.
- Collaborate with team members using communication tools.
- Provide feedback and update task status.

## User Roles

- Super-Admin: Full control over the platform, including user management and system settings.
- Admins: Project and team management, task assignment, and reporting.
- Users: Task execution, collaboration, and feedback.

## Security

### Data Protection
ProjectShala ensures data protection through:

- Encryption: All sensitive data is encrypted.
- Regular Backups: Automatic backups are scheduled to prevent data loss.
- Access Control: Role-based access control to manage permissions.
### Compliance
The platform adheres to industry standards and regulations to ensure compliance and security.


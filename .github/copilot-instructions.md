# Django Social App - Copilot Instructions

## Project Overview
A Django 5.2 social networking application with user authentication. Currently features user login/logout, password management, and a dashboard. Architecture uses Django's built-in authentication system with planned expansion to images and people (social) features.

**Key Technologies**: Django 5.2, SQLite, Django Templates, Bootstrap CSS patterns

## Architecture & Structure

### App Organization
- **config/**: Project configuration (settings, URLs, WSGI)
- **accounts/**: Authentication and user management app
  - Handles login, logout, password changes, dashboard
  - Contains forms, views, templates, and URL routing
  - Uses Django's built-in `auth` views for standard operations

### URL Routing Pattern
- Main router: `config/urls.py` includes `accounts:` namespace
- App routes: `accounts/urls.py` defines `app_name = "accounts"`
- URL naming convention: `path('name/', view, name='route_name')` enables template references via `{% url 'accounts:route_name' %}`

### Authentication Flow
1. User accesses `/accounts/login/` → Django's built-in `LoginView`
2. Custom `LoginForm` validates credentials
3. On success → redirect to `accounts:dashboard` (see `LOGIN_REDIRECT_URL` in settings)
4. Dashboard requires `@login_required` decorator
5. Logout at `/accounts/logout/` → redirect to `accounts:login` (`LOGOUT_REDIRECT_URL`)

## Key Files & Their Responsibilities

| File | Purpose |
|------|---------|
| `config/settings.py` | Database (SQLite), installed apps, redirect URLs, middleware |
| `config/urls.py` | Root URL dispatcher; includes accounts app |
| `accounts/urls.py` | Maps `/accounts/` routes using Django auth views + custom views |
| `accounts/views.py` | Dashboard (protected), custom login handler (currently commented out) |
| `accounts/forms.py` | `LoginForm` with username/password fields |
| `accounts/templates/base.html` | Navigation header with user context, section highlighting |
| `accounts/templates/accounts/dashboard.html` | User dashboard landing page |

## Development Patterns

### Template Context Variables
- Templates receive `section` parameter to highlight active nav item: `{% if section == "dashboard" %}class="selected"{% endif %}`
- User info via `request.user` → `{{ request.user.username }}` or `{{ request.user.firstname }}`
- Static files loaded via `{% load static %}` and `{% static 'path' %}`

### View Decorators
- `@login_required` protects views; redirects to login on access attempt
- Usage: `from django.contrib.auth.decorators import login_required`

### Forms & Validation
- Create forms inheriting from `forms.Form` (not `ModelForm` yet—models are minimal)
- Define fields with widgets for HTML rendering: `forms.TextInput(attrs={'placeholder': '...'})`

### Built-in Auth Views vs Custom
- **Django built-in** (`auth_views`): LoginView, LogoutView, PasswordChangeView
- **Custom** (`dashboard`, `login_view`): When business logic needed beyond defaults
- Currently using built-in `LoginView` on primary `/accounts/login/` route

## Common Tasks

### Add a New Page/Feature
1. Create view in `accounts/views.py` (or new app if needed)
2. Add URL pattern in `accounts/urls.py` with unique `name`
3. Create template in `accounts/templates/accounts/`
4. Extend `base.html` and pass `section="feature_name"` for nav highlighting

### Create a New App
- Run: `python manage.py startapp app_name`
- Add to `INSTALLED_APPS` in `config/settings.py`
- Include app URLs in `config/urls.py`

### Run Development Server
- `python manage.py runserver` (default: http://127.0.0.1:8000/)

### Database Migrations
- After model changes: `python manage.py makemigrations`
- Apply: `python manage.py migrate`

### Create Admin User
- `python manage.py createsuperuser` → access `/admin/`

## Upcoming Features (Template Structure Ready)
- **Images section**: Placeholder in nav (`{% if section == "images" %}`)
- **People section**: Placeholder in nav (`{% if section == "people" %}`)
These are currently stubs; build views/models following the dashboard pattern.

## Important Settings & Configurations
- **DEBUG = True**: Development only; must be False in production
- **SECRET_KEY**: Change before production deployment
- **LOGIN_REDIRECT_URL = 'accounts:dashboard'**: Where users land after login
- **LOGOUT_REDIRECT_URL = 'accounts:login'**: Where users go after logout
- **ALLOWED_HOSTS = []**: Update for production domains

## Code Style & Conventions
- Use Django class-based views for standard CRUD (auth views demonstrate this)
- Use function-based views for simple, custom logic (dashboard, login_view)
- Templates extend `base.html` to maintain consistent UI
- URL names are descriptive and namespaced (`app:action` format)
- Forms use `forms.Form` with explicit field definitions; placeholder text via widget attrs

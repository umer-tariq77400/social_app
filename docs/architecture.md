# Social App Architecture

## Project Overview
A Django-based social networking application that allows users to register, authenticate (including OAuth2 via Google), share images via bookmarklet, follow other users, and view an activity stream.

---

## Technology Stack
- **Framework**: Django 5.2.7
- **Database**: SQLite3 (development)
- **Authentication**: Django Auth + Social Auth (Google OAuth2)
- **Image Processing**: easy_thumbnails
- **Python Version**: Managed via `.python-version`

---

## Application Flow

### 1. User Registration & Authentication Flow
```
User visits site
    ↓
Registration (accounts/register/) OR Login (accounts/login/)
    ↓
Profile created automatically
    ↓
Redirect to Dashboard (accounts/)
```

### 2. OAuth2 Flow (Google)
```
User clicks "Login with Google"
    ↓
Redirect to Google OAuth (oauth/)
    ↓
Social Auth Pipeline executes:
    - Check if user exists by email
    - Create/retrieve user
    - Create/retrieve profile
    - Associate social account
    ↓
Redirect to Dashboard
```

### 3. Image Bookmarking Flow
```
User activates bookmarklet on external site
    ↓
Bookmarklet launcher opens popup
    ↓
Image create form (images/create/)
    ↓
Image downloaded and saved
    ↓
Action created ("bookmarked image")
    ↓
Redirect to image detail page
```

### 4. Social Interaction Flow
```
User views user list (accounts/users/)
    ↓
Clicks on user profile (accounts/users/<username>/)
    ↓
Follow/Unfollow via AJAX (accounts/users/follow/)
    ↓
Contact relationship created/deleted
    ↓
Action created ("is following")
    ↓
Activity stream updated
```

### 5. Activity Stream Flow
```
Dashboard loads (accounts/)
    ↓
Fetch actions from followed users
    ↓
Display recent activities (last 10)
    ↓
Activities include: account creation, following, image bookmarking, image liking
```

---

## Project Structure

### Root Configuration (`config/`)
- **settings.py**: Main settings, installed apps, middleware, authentication backends
- **urls.py**: Root URL configuration
- **wsgi.py**: WSGI application entry point

### Apps

#### 1. **accounts** (User Management)
**Models** (`accounts/models.py`):
- `Profile`: User profile with photo and date_of_birth
- `Contact`: Many-to-many relationship for user following

**Views** (`accounts/views.py`):
- `register`: User registration
- `dashboard`: User dashboard with activity stream and bookmarklet code
- `edit`: Edit user profile
- `user_list`: List all active users
- `user_detail`: Display user profile
- `user_follow`: AJAX endpoint for follow/unfollow
- `disconnect_social`: Disconnect OAuth provider

**Forms** (`accounts/forms.py`):
- `LoginForm`: User login
- `UserRegistrationForm`: New user registration
- `UserEditForm`: Edit user details
- `ProfileEditForm`: Edit profile details

**Authentication** (`accounts/authentication.py`):
- `EmailAuthBackend`: Authenticate via email
- `get_or_create_user_by_email`: OAuth pipeline - find existing user by email
- `create_profile`: OAuth pipeline - create profile after social auth
- `disconnect_profile`: OAuth pipeline - handle disconnection

**URLs** (`accounts/urls.py`):
- `/accounts/` → dashboard
- `/accounts/register/` → register
- `/accounts/edit/` → edit
- `/accounts/disconnect/<backend>/` → disconnect_social
- `/accounts/users/` → user_list
- `/accounts/users/follow/` → user_follow
- `/accounts/users/<username>/` → user_detail
- `/accounts/` (includes django.contrib.auth.urls for login/logout/password reset)

**Templates** (`accounts/templates/`):
- `base.html`: Base template for all pages
- `accounts/dashboard.html`: User dashboard
- `accounts/edit.html`: Profile edit form
- `accounts/register.html`: Registration form
- `accounts/register_done.html`: Registration success
- `accounts/disconnect_confirm.html`: OAuth disconnect confirmation
- `accounts/user/list.html`: User list
- `accounts/user/detail.html`: User profile detail
- `registration/login.html`: Login page
- `registration/logout.html`: Logout confirmation
- `registration/password_change_form.html`: Password change form
- `registration/password_change_done.html`: Password change success
- `registration/password_reset_form.html`: Password reset request
- `registration/password_reset_email.html`: Password reset email template
- `registration/password_reset_done.html`: Password reset email sent
- `registration/password_reset_confirm.html`: Password reset confirmation
- `registration/password_reset_complete.html`: Password reset complete

**Static Files**:
- CSS:
  - `accounts/static/css/base.css`: Base styles
  - `accounts/static/css/user_list.css`: User list styles
  - `accounts/static/css/user_detail.css`: User detail styles
  - `accounts/static/accounts/css/dashboard.css`: Dashboard styles
  - `accounts/static/accounts/css/disconnect.css`: Disconnect page styles
- JS:
  - `accounts/static/accounts/js/follow.js`: Follow/unfollow functionality

#### 2. **images** (Image Bookmarking)
**Models** (`images/models.py`):
- `Image`: Bookmarked images with title, description, url, image file, and likes

**Views** (`images/views.py`):
- `image_create`: Create new bookmarked image (via bookmarklet or form)
- `image_list`: Paginated list of images (supports AJAX)
- `image_detail`: Image detail view
- `image_like`: AJAX endpoint for liking/unliking images

**Forms** (`images/forms.py`):
- `ImageCreateForm`: Create image by downloading from URL

**URLs** (`images/urls.py`):
- `/images/` → image_list
- `/images/create/` → image_create
- `/images/<id>/<slug>/` → image_detail
- `/images/like/` → image_like

**Templates** (`images/templates/images/image/`):
- `list.html`: Image list with infinite scroll
- `list_images.html`: Partial template for AJAX image loading
- `create.html`: Image creation form
- `detail.html`: Image detail with like button
- `bookmarklet_launcher.js`: Bookmarklet JavaScript code

**Static Files**:
- CSS:
  - `images/static/images/css/image_card.css`: Image card styles
  - `images/static/css/bookmarklet.css`: Bookmarklet popup styles
- JS:
  - `images/static/js/bookmarklet.js`: Bookmarklet functionality

#### 3. **actions** (Activity Stream)
**Models** (`actions/models.py`):
- `Action`: Generic activity tracking with user, verb, target (GenericForeignKey)

**Utils** (`actions/utils.py`):
- `create_action`: Create action with duplicate prevention (1-minute window)

**Admin** (`actions/admin.py`):
- `ActionAdmin`: Admin interface for actions

**URLs**: None (no public views)

**Views** (`actions/views.py`): Empty (no views)

**Templates**: None

**Static Files**: None

---

## Global Static Files (`static/`)
- **JS**:
  - `static/js/csrf.js`: CSRF token handling
  - `static/js/messages.js`: Django messages display

---

## URL Routing Map

### Root URLs (`config/urls.py`)
```
/admin/                     → Django admin
/accounts/                  → accounts app URLs
/oauth/                     → social_django URLs
/images/                    → images app URLs
/media/                     → Media files (DEBUG only)
```

### Accounts URLs (`accounts/urls.py`)
```
/accounts/                              → dashboard
/accounts/login/                        → login (Django auth)
/accounts/logout/                       → logout (Django auth)
/accounts/password_change/              → password change (Django auth)
/accounts/password_change/done/         → password change done (Django auth)
/accounts/password_reset/               → password reset (Django auth)
/accounts/password_reset/done/          → password reset done (Django auth)
/accounts/reset/<uidb64>/<token>/       → password reset confirm (Django auth)
/accounts/reset/done/                   → password reset complete (Django auth)
/accounts/register/                     → register
/accounts/edit/                         → edit
/accounts/disconnect/<backend>/         → disconnect_social
/accounts/users/                        → user_list
/accounts/users/follow/                 → user_follow
/accounts/users/<username>/             → user_detail
```

### Images URLs (`images/urls.py`)
```
/images/                    → image_list
/images/create/             → image_create
/images/<id>/<slug>/        → image_detail
/images/like/               → image_like
```

### OAuth URLs (`social_django`)
```
/oauth/login/<backend>/     → OAuth login
/oauth/complete/<backend>/  → OAuth callback
/oauth/disconnect/<backend>/ → OAuth disconnect
```

---

## Database Models

### User (Django built-in)
Extended with:
- `following`: ManyToManyField through Contact model

### Profile (accounts.models.Profile)
```
- user: OneToOneField(User)
- date_of_birth: DateField (optional)
- photo: ImageField (optional)
```

### Contact (accounts.models.Contact)
```
- user_from: ForeignKey(User)
- user_to: ForeignKey(User)
- created: DateTimeField
```

### Image (images.models.Image)
```
- user: ForeignKey(User)
- title: CharField
- description: TextField
- slug: SlugField (auto-generated)
- url: URLField
- image: ImageField
- created: DateTimeField
- users_like: ManyToManyField(User)
```

### Action (actions.models.Action)
```
- user: ForeignKey(User)
- verb: CharField
- created: DateTimeField
- target_ct: ForeignKey(ContentType) - for GenericForeignKey
- target_id: PositiveIntegerField - for GenericForeignKey
- target: GenericForeignKey
```

---

## Authentication System

### Authentication Backends
1. **ModelBackend**: Default Django username/password
2. **EmailAuthBackend**: Custom email/password authentication
3. **GoogleOAuth2**: Google OAuth2 authentication

### Social Auth Pipeline
```
1. social_details
2. social_uid
3. auth_allowed
4. social_user
5. get_username
6. get_or_create_user_by_email (CUSTOM)
7. create_user
8. create_profile (CUSTOM)
9. associate_user
10. load_extra_data
11. user_details
```

### Disconnect Pipeline
```
1. allowed_backends
2. get_users
3. disconnect_profile (CUSTOM)
4. disconnect
```

### Login/Logout Settings
- `LOGIN_REDIRECT_URL`: dashboard
- `LOGOUT_REDIRECT_URL`: login
- `LOGOUT_URL`: logout

---

## Key Features

### 1. Bookmarklet
- JavaScript bookmarklet that can be dragged to browser bookmarks bar
- Opens popup window with image selection from current page
- Submits selected image to `/images/create/`
- Downloads and saves image to media storage

### 2. Activity Stream
- Tracks user actions: account creation, following, image bookmarking, image liking
- Displays activities from followed users on dashboard
- Uses GenericForeignKey for flexible target objects
- Prevents duplicate actions within 1-minute window

### 3. Follow System
- Users can follow/unfollow other users
- AJAX-based for seamless UX
- Contact model tracks relationships
- Following/followers accessible via User model

### 4. Image Management
- Download images from external URLs
- Automatic slug generation from title
- Like/unlike functionality via AJAX
- Paginated list with infinite scroll support
- Thumbnail generation via easy_thumbnails

### 5. Profile Management
- Automatic profile creation on registration and OAuth
- Profile photo upload
- Edit user details and profile separately
- OAuth account linking and unlinking

---

## Data Flow Diagrams

### Image Creation Flow
```
External Website
    ↓ (User activates bookmarklet)
Bookmarklet JS (images/static/js/bookmarklet.js)
    ↓ (Opens popup with image selection)
Image Create Form (images/create/)
    ↓ (POST with image URL)
ImageCreateForm.save()
    ↓ (Downloads image via requests)
Image Model saved
    ↓
create_action("bookmarked image")
    ↓
Redirect to Image Detail
```

### Follow/Unfollow Flow
```
User Detail Page (accounts/users/<username>/)
    ↓ (User clicks follow/unfollow button)
AJAX Request (accounts/static/accounts/js/follow.js)
    ↓ (POST to /accounts/users/follow/)
user_follow view
    ↓
Contact.objects.create() or .delete()
    ↓
create_action("is following") [if follow]
    ↓
JSON Response {"status": "ok"}
    ↓
Button UI updated
```

### Dashboard Activity Stream
```
Dashboard View (accounts/)
    ↓
Action.objects.exclude(user=request.user)
    ↓
Filter by following_ids
    ↓
Select/prefetch related objects
    ↓
Render last 10 actions
```

---

## Static File Organization

### Global Static Files
- `/static/js/csrf.js`: CSRF token for AJAX
- `/static/js/messages.js`: Auto-dismiss Django messages

### App-Specific Static Files

#### Accounts
- `/accounts/static/css/base.css`: Global base styles
- `/accounts/static/css/user_list.css`: User list page
- `/accounts/static/css/user_detail.css`: User detail page
- `/accounts/static/accounts/css/dashboard.css`: Dashboard page
- `/accounts/static/accounts/css/disconnect.css`: Disconnect confirmation
- `/accounts/static/accounts/js/follow.js`: Follow/unfollow AJAX

#### Images
- `/images/static/images/css/image_card.css`: Image card component
- `/images/static/css/bookmarklet.css`: Bookmarklet popup
- `/images/static/js/bookmarklet.js`: Bookmarklet functionality

---

## Template Hierarchy

```
base.html (accounts/templates/base.html)
    ├── accounts/dashboard.html
    ├── accounts/edit.html
    ├── accounts/register.html
    ├── accounts/register_done.html
    ├── accounts/disconnect_confirm.html
    ├── accounts/user/list.html
    ├── accounts/user/detail.html
    ├── registration/login.html
    ├── registration/logout.html
    ├── registration/password_*.html
    ├── images/image/list.html
    ├── images/image/create.html
    └── images/image/detail.html
```

---

## Security Features

1. **CSRF Protection**: All POST requests protected via CSRF tokens
2. **Login Required**: Most views require authentication via `@login_required`
3. **Password Validation**: Django's built-in password validators
4. **Email Uniqueness**: Enforced in registration and profile edit
5. **OAuth Security**: Social auth pipeline with custom email matching
6. **Profile Preservation**: Profiles not deleted on OAuth disconnect

---

## Third-Party Integrations

### 1. Social Django (OAuth2)
- **Provider**: Google OAuth2
- **Configuration**: `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY`, `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET`
- **Custom Pipeline**: Email-based user matching, profile creation

### 2. Easy Thumbnails
- **Purpose**: Image thumbnail generation
- **Aliases**: `avatar` (64x64), `avatar_large` (200x200)
- **Crop**: Center crop

### 3. Django Extensions
- **Purpose**: Development utilities

---

## Media Files

- **MEDIA_URL**: `/media/`
- **MEDIA_ROOT**: `BASE_DIR/media/`
- **Upload Paths**:
  - User photos: `users/%Y/%m/%d/`
  - Bookmarked images: `images/%Y/%m/%d/`

---

## Development Notes

1. **Email Backend**: Console backend for development (password reset emails)
2. **Debug Mode**: Enabled in development
3. **Allowed Hosts**: localhost, mysite.com, 127.0.0.1
4. **Database**: SQLite3 for development
5. **Static Files**: Served via Django in DEBUG mode
6. **Media Files**: Served via Django in DEBUG mode

---

## Future Considerations

1. **Production Database**: Migrate to PostgreSQL
2. **Static Files**: Use CDN or separate static file server
3. **Media Files**: Use cloud storage (S3, etc.)
4. **Caching**: Implement Redis for activity stream and user queries
5. **Search**: Add search functionality for users and images
6. **Notifications**: Real-time notifications for follows and likes
7. **API**: RESTful API for mobile apps

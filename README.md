# Django Social App

A modern Django 5.2 social networking platform where users can discover, bookmark, and share images with a real-time activity stream. Built with a focus on user engagement through following, liking, and social discovery.

## Features

- **User Authentication**
  - Email/password registration and login
  - Google OAuth2 integration
  - Email-based authentication backend

- **Image Management**
  - Bookmark images via drag-and-drop bookmarklet
  - Download images from URLs or upload directly
  - Image discovery and browsing
  - Like/ranking system with total counts

- **Social Features**
  - Follow/unfollow users
  - Real-time activity stream showing followed users' actions
  - View tracking with Redis caching
  - User profiles with customizable information

- **Bookmarklet**
  - One-click image bookmarking from any website
  - Automatic image download and storage
  - Instant activity logging

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Django 5.2 |
| **Database** | PostgreSQL (prod) / SQLite (dev) |
| **Cache** | Redis |
| **Authentication** | Django built-in + social-auth-app-django (Google OAuth2) |
| **Frontend** | Tailwind CSS, JavaScript |
| **File Storage** | Local filesystem (dev) / Azure Blob Storage (prod) |
| **Image Processing** | Pillow, easy-thumbnails |
| **Deployment** | Heroku, WhiteNoise |

## Project Structure

```
social_app/
├── accounts/              # User auth, profiles, follow relationships
├── images/                # Image CRUD, likes, bookmarklet handling
├── actions/               # Activity stream log via GenericForeignKey
├── pages/                 # Landing page
├── theme/                 # Tailwind CSS compilation
├── config/                # Django settings, URLs, WSGI
├── templates/             # Base templates + app-specific
├── static/                # CSS, JavaScript, bookmarklet code
├── media/                 # User uploads (images, avatars)
├── manage.py              # Django CLI
└── pyproject.toml         # Project dependencies
```

## Quick Start

### Prerequisites
- Python 3.13+
- pip or poetry
- PostgreSQL (production)
- Redis (optional, recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/umer-tariq77400/social_app.git
   cd social_app
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   ```

4. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

   Visit `http://localhost:8000` in your browser.

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Debug mode
DEBUG=True

# Database (production uses DATABASE_URL)
# Leave unset for SQLite in development

# Redis (optional for development)
REDIS_URL=redis://localhost:6379/0

# Google OAuth2 (required for OAuth features)
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=your-client-id
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your-client-secret

# Azure Storage (production only)
AZURE_STORAGE_ACCOUNT_NAME=your-account
AZURE_STORAGE_ACCOUNT_KEY=your-key
AZURE_STORAGE_CONTAINER_NAME=social-app-media
```

### Development Setup

- **Database**: SQLite (automatic)
- **Media Storage**: Local filesystem (`media/` directory)
- **Redis**: Optional; gracefully falls back to 0 view counts if unavailable

### Production Setup

- **Database**: PostgreSQL (via `DATABASE_URL`)
- **Media Storage**: Azure Blob Storage
- **Redis**: RedisCloud (via `REDISCLOUD_URL`)
- **Static Files**: WhiteNoise (included in MIDDLEWARE)

## Key Concepts

### Activity Stream
Uses Django's `GenericForeignKey` to track heterogeneous actions (bookmarks, follows, likes). Actions are automatically deduplicated within 60-second windows to prevent spam in the activity feed.

**Example**: When a user bookmarks an image, an action is created with:
- User: the person who bookmarked
- Verb: "bookmarked image"
- Target: the Image object

### Follow System
Self-referential many-to-many relationship through the `Contact` model. The User model is dynamically extended with a `following` field at startup.

**Dashboard shows**:
- Last 10 actions from users you follow
- Your own images and actions
- Real-time view counts for images

### View Tracking with Redis
Each image view increments a Redis counter at `image:{id}:views`. Views are retrieved efficiently using Redis pipelines in list views.

**Graceful Degradation**: If Redis is unavailable, the app defaults to 0 views per image.

### OAuth2 Pipeline
Custom pipeline functions prevent duplicate users on OAuth reconnect by matching on email address. Profiles are automatically created after signup to avoid OneToOne errors.

## Common Tasks

### Add a New Feature

1. **Extend a model**
   ```bash
   # 1. Edit the model in the app's models.py
   # 2. Create a migration
   python manage.py makemigrations [app_name]
   # 3. Apply the migration
   python manage.py migrate
   ```

2. **Update forms** (if user-facing)
   - Edit `forms.py` in the app
   - Add CSS classes via `widget.attrs` for Tailwind styling

3. **Update views**
   - Edit `views.py`
   - Protect with `@login_required` if needed

4. **Update templates**
   - Edit or create templates in `app/templates/app/`
   - Extend `templates/base.html`

### Rebuild Tailwind CSS

After editing `theme/static_src/src/styles.css`:

```bash
python manage.py tailwind build
```

### Run Tests

```bash
# All tests
python manage.py test

# Specific app
python manage.py test images

# Specific test class
python manage.py test images.ImageModelTests
```

### Access Django Admin

1. Create a superuser if you haven't already:
   ```bash
   python manage.py createsuperuser
   ```

2. Visit `http://localhost:8000/admin/` and log in

### Use the Django Shell

```bash
python manage.py shell
```

Example: Get the 10 most-liked images:
```python
from images.models import Image
Image.objects.order_by('-total_likes')[:10]
```

## Testing

The project includes comprehensive tests in each app. Run tests with:

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test [app_name]

# Run specific test class
python manage.py test [app].[TestClass]

# Run specific test method
python manage.py test [app].[TestClass].[test_method]
```

Tests use fixtures and mocking patterns. Always create test users/images in `setUp()`. Tests automatically rollback database changes after each test.

## HTTPS Development

For local HTTPS testing (useful for OAuth2):

1. **Generate a self-signed certificate** (see `DEVELOPMENT.md`)
2. Run the SSL development server:
   ```bash
   python manage.py runsslserver
   ```

## Deployment

### Heroku

The project includes `Procfile` and `heroku.yml` for Heroku deployment:

```bash
heroku create your-app-name
git push heroku master
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Manual Deployment

1. Set environment variables on your server
2. Install dependencies: `pip install -e .`
3. Collect static files: `python manage.py collectstatic --noinput`
4. Run migrations: `python manage.py migrate`
5. Start Gunicorn: `gunicorn config.wsgi:application`

## Troubleshooting

### 60-Second Action Deduplication

If testing the activity stream, identical actions (same user, verb, target) within 60 seconds are silently deduplicated. Either:
- Wait 60 seconds between actions, or
- Manipulate timestamps in the Django shell to test

### Follow System Not Working

Ensure `accounts` app comes BEFORE `django.contrib.auth` in `INSTALLED_APPS`. This order is critical—moving it breaks the User model extension.

### No View Counts Showing

- Check Redis is running: `redis-cli ping` should return `PONG`
- Or ensure Redis fallback is working (should show 0 views if Redis unavailable)
- Check for errors in Django logs

### Images Not Downloading from Bookmarklet

1. Verify `static/js/bookmarklet_launcher.js` exists
2. Check image URL is valid
3. Ensure image format is jpg, jpeg, or png
4. Check Django logs for validation errors

## Project Layout: Key Files

| File/Directory | Purpose |
|---|---|
| `config/settings.py` | Main Django settings; INSTALLED_APPS order critical here |
| `config/urls.py` | Root URL dispatcher |
| `accounts/authentication.py` | Custom auth backends and OAuth2 pipeline functions |
| `accounts/models.py` | User model extension (following field), Profile, Contact models |
| `images/forms.py` | ImageCreateForm with URL download logic |
| `actions/utils.py` | `create_action()` helper with deduplication logic |
| `static/js/bookmarklet_launcher.js` | Bookmarklet code served to users |
| `DEVELOPMENT.md` | Local development setup and HTTPS certificate generation |

## API Reference

### Views

**Images**
- `GET /images/` — List all images (paginated)
- `GET /images/<id>/<slug>/` — View image detail
- `POST /images/create/` — Create new image (bookmarklet or form)
- `POST /images/<id>/like/` — Like/unlike an image (AJAX)

**Accounts**
- `GET /accounts/dashboard/` — User dashboard with activity stream
- `GET /accounts/edit/` — Edit profile
- `GET /accounts/users/` — List all users
- `GET /accounts/users/<username>/` — View user profile
- `POST /accounts/users/follow/` — Follow/unfollow user (AJAX)
- `GET /accounts/register/` — User registration

**Auth**
- `POST /accounts/login/` — User login
- `GET /accounts/logout/` — User logout
- `GET /accounts/password_reset/` — Password reset

## Developer Guide

For comprehensive development guidance on architecture, patterns, and conventions, see **[`.github/copilot-instructions.md`](.github/copilot-instructions.md)**. This guide includes:

- **Architecture Overview**: Five core apps with clear responsibility boundaries
- **Critical Patterns**: Activity Stream via GenericForeignKey, Follow Graph, Redis caching, OAuth2 pipeline
- **Data Flows**: Complete end-to-end flows (Bookmarklet → Image → Action, Follow System, Dashboard Activity Stream)
- **Code Conventions**: Views, Forms, Models, Templates, AJAX, Redis usage, Signals, Error handling
- **Implementation Details**: Image download validation, view count tracking, action deduplication
- **Debugging Gotchas**: INSTALLED_APPS ordering, OAuth reconnect, Profile creation, Redis fallback

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -am 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request

**Before contributing**, read the Developer Guide above for project-specific patterns and conventions.

## License

This project is open source and available under the MIT License.

## Contact

For questions or support, open an issue on GitHub or contact the maintainer.

---

**Built with ❤️ using Django 5.2**

# Django Social App - Copilot Instructions

## Project Overview
A Django 5.2 social networking application featuring user authentication (email + Google OAuth2), image bookmarking via bookmarklet, user follow/social features, and a real-time activity stream. Tech stack: Django 5.2, PostgreSQL (prod)/SQLite (dev), Redis for view tracking, Tailwind CSS, social-auth-app-django.

## Architecture Overview

### Five Core Apps
1. **accounts**: User auth, profiles, follow relationships → dashboard shows activity stream of followed users
2. **images**: Bookmarklet-driven image capture + like/ranking system with Redis view tracking
3. **actions**: Generic activity log (user-agnostic) via ContentType — used by accounts & images
4. **pages**: Landing page (minimal)
5. **theme**: Tailwind CSS compilation (static bundling)

### Critical Architectural Patterns

**Activity Stream Pattern** (`actions/models.py`): Uses `GenericForeignKey` (ContentType + target_id) to track heterogeneous actions. Actions are deduped within 1-minute windows per user+verb+target (`actions/utils.py:create_action`). Used for dashboard feeds, follow notifications, and like history.

**Follow Graph** (`accounts/models.Contact`): Self-referential many-to-many via through-model tracks followers. User model extended with `following` field dynamically in `accounts/models.py`. Dashboard filters actions to `following_ids` + self.

**Redis Caching**: View counts live in Redis (`image:{id}:views` keys), incremented on each image detail view. Images use pipeline queries for efficiency. Graceful fallback to 0 views if Redis unavailable.

**OAuth2 Pipeline Customization**: Custom social auth pipeline (`accounts/authentication.py`) intercepts Google login to:
  - Match existing users by email (prevents duplicates on reconnect)
  - Auto-create profiles (not done by defaults)
  - Preserve profile data on disconnect (never delete)

## Key Files & Patterns

| File | Responsibility |
|------|---|
| `config/settings.py` | INSTALLED_APPS order matters: accounts before contrib.auth for User.add_to_class(). Redis/Azure configs for prod. |
| `config/urls.py` | Root dispatcher includes all apps. Note: `include("django.contrib.auth.urls")` in accounts/urls.py handles /login/, /logout/, /password_reset/. |
| `accounts/views.py` | `dashboard`: activity stream + bookmarklet code. `user_detail/user_list`: paginated with Redis view counts. `user_follow`: AJAX Contact CRUD. |
| `accounts/authentication.py` | OAuth pipeline: `get_or_create_user_by_email`, `create_profile`, `disconnect_profile`. EMAIL backend for non-OAuth login. |
| `accounts/models.py` | User.add_to_class("following", ...) modifies Django's User. Contact = through-model for following. Profile has OneToOne to User. |
| `images/views.py` | Image CRUD (create downloads via requests library). Like/ranking via Redis. Supports `?images_only=1` AJAX partial loading. |
| `images/signals.py` | `users_like_changed` signal syncs total_likes count on m2m changes. |
| `images/forms.py` | `ImageCreateForm` downloads image from URL with error handling. Validates extensions (jpg/jpeg/png only). |
| `actions/utils.py` | `create_action`: dedupe logic—doesn't create if identical action within last 60 seconds. |

## Authentication & Authorization

**Three backends** (settings.AUTHENTICATION_BACKENDS):
1. ModelBackend (username/password) — Django built-in
2. EmailAuthBackend — custom (`accounts/authentication.py`): authenticate via email as username
3. GoogleOAuth2 — via python-social-auth

**Social Auth Pipeline** (settings.SOCIAL_AUTH_PIPELINE):
- Calls custom `get_or_create_user_by_email` after social details parsed → finds existing User by email
- Calls custom `create_profile` after User creation → ensures Profile exists
- Calls custom `disconnect_profile` on OAuth disconnect → intentionally does NOT delete profile

**Protecting Views**:
- Use `@login_required` decorator (redirects to /accounts/login/)
- Most AJAX endpoints (follow, like) also `@login_required`

## Data Flow: Bookmarklet → Image → Action

1. User drags bookmarklet to browser toolbar
2. On external site, user clicks bookmarklet → opens popup with `images/templates/bookmarklet_launcher.js`
3. Popup selects image and submits to `/images/create/?url=...&title=...`
4. `image_create` view: ImageCreateForm downloads image via requests, saves to media/images/
5. `create_action(user, "bookmarked image", image_obj)` logs activity
6. Redirects to `/images/{id}/{slug}/` → increments Redis view counter
7. Dashboard shows "User bookmarked Image" in activity stream for followers

## Data Flow: Follow System

1. User clicks follow button on `/accounts/users/{username}/` (user_detail view)
2. AJAX POST to `/accounts/users/follow/` with action=follow & id={user_id}
3. `user_follow` view: `Contact.objects.create(user_from=request.user, user_to=...)`
4. `create_action(request.user, "is following", target_user)` logs activity
5. Dashboard refreshes → followers see "User is following Other User" in stream

## Data Flow: Activity Stream (Dashboard)

1. `dashboard` view fetches `request.user.following.all()` (via Contact model)
2. Queries `Action.objects.filter(user_id__in=following_ids)` with `select_related("user", "user__profile").prefetch_related("target")`
3. Gets last 10 actions ordered by `-created`
4. Renders action verb + target link (e.g., "john likes [image]")
5. Also displays user's own images with Redis view counts

## Common Development Tasks

### Add Image Feature (e.g., Filter, Tags)
1. Extend `Image` model in `images/models.py` (add field, create migration)
2. Update `ImageCreateForm` if new user-input fields
3. Update `images/views.py` (filter in `image_list`, pass to templates)
4. Create/update templates in `images/templates/images/image/`
5. If adding likes or bookmarks, wrap in `create_action()` call

### Add Profile Fields
1. Extend `Profile` model (`accounts/models.py`)
2. Create migration: `python manage.py makemigrations accounts`
3. Update `ProfileEditForm` in `accounts/forms.py` to include new fields
4. Update `accounts/templates/accounts/edit.html`
5. Run `python manage.py migrate`

### Implement New Action Type
1. Call `create_action(user, "verb_string", optional_target_obj)` in relevant view
2. Create template in `actions/templates/actions/action/` to render action + target
3. Include template in `accounts/templates/accounts/dashboard.html` action loop
4. Action deduplication is automatic (1-minute window)

## Implementation Details for Common Tasks

### Image Download & Validation (`images/forms.py`)
- `ImageCreateForm.save()` downloads images via `requests` library with User-Agent header
- Detects file type from `Content-Type` response header (fallback: URL extension)
- Valid types: jpg, jpeg, png only
- Converts downloaded bytes to Django `ContentFile` before saving
- Timeout: 10 seconds; raises `ValidationError` on failure
- Both URL and file upload paths supported; validator requires at least one

### View Count Tracking (`images/views.py`, `accounts/views.py`)
- Redis key format: `image:{id}:views` (e.g., `image:42:views`)
- Incremented on `image_detail` view (every visit)
- Retrieved via Redis pipeline for efficiency in list/paginated views
- Pipeline pattern: `r.pipeline(); for img in images: pipeline.get(...); view_counts = pipeline.execute()`
- Graceful degradation: missing Redis key returns `None`, handled as `0 views`
- Always wrap in try-except; exceptions silently fallback to `views=0`

### Action Deduplication (`actions/utils.py`)
- `create_action(user, verb, target=None)` prevents duplicate actions within 60-second window
- Deduplication checks: user_id, verb, AND (if target) target_ct + target_id
- Uses `timezone.now() - timedelta(minutes=1)` for window boundary
- Returns action object if created; None if deduplicated
- Call this in views after Follow/Like/Bookmark actions for activity stream

## Quick Start & Essential Commands

```bash
# Setup (first time)
pip install -e .                              # Install dependencies from pyproject.toml
python manage.py migrate                      # Apply migrations
python manage.py createsuperuser              # Create admin user

# Development
python manage.py runserver                    # Dev server (SQLite, local media)
python manage.py makemigrations [app]         # Create migration files
python manage.py migrate                      # Apply migrations
python manage.py shell                        # Django shell (for testing queries/logic)
python manage.py tailwind build               # Rebuild CSS (edit theme/static_src/src/styles.css first)
python manage.py test                         # Run all tests
python manage.py test [app].[TestClass]       # Run specific test class

# HTTPS Testing (requires cert.crt, cert.key - see DEVELOPMENT.md)
python manage.py runsslserver

# Admin
http://localhost:8000/admin/                  # Django admin (superuser only)
```

## Critical Gotchas & Debugging

**INSTALLED_APPS order**: `accounts` MUST come BEFORE `django.contrib.auth` so `User.add_to_class("following", ...)` executes on Django startup. Moving `accounts` after `contrib.auth` breaks the entire follow system. This is enforced in `accounts/models.py` line 4-9.

**OAuth Reconnect**: If user disconnects then reconnects Google OAuth, the `get_or_create_user_by_email` pipeline function matches by email to prevent duplicate users. Without this, same email would create new User. See `accounts/authentication.py:get_or_create_user_by_email()`.

**Profile Creation**: `create_profile` pipeline ensures Profile exists after OAuth signup. If this fails, users can register but have no Profile → `profile.py` OneToOne access fails. Always check for profile existence or create in migrations if needed. See `accounts/authentication.py:create_profile()`.

**Action Deduplication**: The 60-second window is strict. Identical follow/like actions within 60s are silently deduplicated. If testing, wait 60s or manipulate `timezone.now()` in shell. See `actions/utils.py:create_action()`.

**Redis Fallback**: All Redis calls fail gracefully to `views=0`. If you forget try-except, code crashes in production. Test without Redis running to catch issues early. Pattern: `try: r.get(...) except Exception: ...` (no logging, silent fallback).

**BookmarkLet Code**: The bookmarklet JavaScript is loaded from disk (`static/js/bookmarklet_launcher.js`) at view time and prefixed with `javascript:` in `accounts/views.py:dashboard()`. If bookmarklet fails, check file exists, is valid JS, and all variables are defined.

**Testing**: Use `python manage.py test [app].[TestClass].[test_method]` for specific tests. Tests use fixtures and mocking (see `images/tests.py` for request/mock patterns). Always use `setUp()` to create test users/images. Tests auto-rollback database after each test.

## Deployment & Azure Integration

**Production Environment**:
- Uses PostgreSQL (connected via `DATABASE_URL` env var)
- Media storage → Azure Blob Storage via `django-storages[azure]`
- Redis from RedisCloud (via `REDISCLOUD_URL`)
- Heroku deployment (see `Procfile`, `heroku.yml`)
- Static files served via WhiteNoise

**Configuring Azure Storage**: Set these env vars:
- `AZURE_STORAGE_ACCOUNT_NAME`
- `AZURE_STORAGE_ACCOUNT_KEY`
- `AZURE_STORAGE_CONTAINER_NAME` (defaults to `social-app-media`)

**Local Development Setup**:
1. Create `.env` file with `DEBUG=True` (or omit for defaults)
2. Uses SQLite by default; no DATABASE_URL needed
3. Uses local filesystem for media (FileSystemStorage)
4. Redis optional for dev; view counts fallback to 0 if unavailable
5. For HTTPS testing: run `python manage.py runsslserver` (requires self-signed cert)

## Important Settings

| Setting | Value | Purpose |
|---------|-------|---------|
| DEBUG | False in prod, True in dev | Template error details, static file serving |
| DATABASES | PostgreSQL in prod, SQLite in dev | config/settings.py auto-switches via dj_database_url |
| MEDIA_URL / MEDIA_ROOT | /media/, BASE_DIR/media/ | User uploads (images, profiles). Prod uses Azure Blob Storage |
| MEDIA_STORAGE | FileSystemStorage (dev), AzureStorage (prod) | Configured in settings via STORAGES dict |
| REDIS_URL | redis://localhost:6379/0 (dev), REDISCLOUD_URL (prod) | View counter cache. Gracefully falls back to 0 if unavailable |
| SOCIAL_AUTH_GOOGLE_OAUTH2_KEY/SECRET | From Google Cloud Console | OAuth provider credentials |
| LOGIN_REDIRECT_URL | 'dashboard' | Redirect after successful login |
| LOGOUT_REDIRECT_URL | 'logout' | Redirect after logout |
| INSTALLED_APPS order | accounts before contrib.auth | **Critical**: allows User.add_to_class() for 'following' field |
| AUTHENTICATION_BACKENDS | ModelBackend, EmailAuthBackend, GoogleOAuth2 | Three backends in order: username, email, then OAuth2 |
| SOCIAL_AUTH_PIPELINE | Custom functions + defaults | Includes `get_or_create_user_by_email`, `create_profile`, `disconnect_profile` |

## Code Conventions

**Views**: Function-based for lightweight logic. Decorate with `@login_required` for protected endpoints. AJAX views return `JsonResponse({"status": "ok"})`. Support `?images_only=1` style GET params for partial template selection (e.g., `image_list` returns paginated grid or empty string on empty final page). For GET params with form data, use `initial=request.GET` instead of `data=request.GET` to avoid validation triggers.

**Forms**: Use `ModelForm` when tied to model (UserEditForm, ImageCreateForm). Always add CSS classes via `widget.attrs` for Tailwind (e.g., `"class": "form-control"`). ImageCreateForm validates one of `url` or `file` exists in `clean()`. The `save()` method downloads images via requests with User-Agent header, detects type from Content-Type, validates jpg/jpeg/png only, converts to ContentFile, times out at 10 seconds.

**Models**: Define `Meta.indexes` on frequently queried fields (`-created`, `-total_likes`). Use `slug` for SEO URLs; auto-populate in `save()` via `slugify()`. Use `GenericForeignKey` (ContentType + target_id) for heterogeneous relationships (Action → Image/User). Leverage `m2m_changed` signals to sync derived fields (total_likes).

**Templates**: Extend `templates/base.html`. Pass `section="app_name"` to highlight nav. Render image objects with `image.views` (populated by views after Redis lookup). Render actions with action verb + target link, using action templates in `actions/templates/actions/action/`.

**AJAX**: POST endpoints use `request.POST.get("action")` to determine operation (e.g., "follow", "unfollow"). Return JsonResponse. List views support pagination via GET param `page`.

**Redis Usage**: Initialize at module level: `r = redis.from_url(settings.REDIS_URL)`. Always wrap calls in try-except; silently fallback to sensible defaults (0 counts) if unavailable. Pipeline queries: `pipeline = r.pipeline(); [pipeline.get(...) for img in images]; pipeline.execute()` to fetch multiple keys efficiently. Key format: `image:{id}:views`.

**Signals**: Use `m2m_changed` signals to sync derived fields (e.g., `total_likes` on `Image` model in `images/signals.py`). Always connect signals in `apps.py` via `ready()` method to avoid duplicate registrations.

**Error Handling Pattern**: Wrap external API calls (requests library, Redis) in try-except with descriptive messages. For user-facing errors, use `messages.error(request, "...")`. For form validation, raise `forms.ValidationError(...)`. Never let external service failures crash the app.

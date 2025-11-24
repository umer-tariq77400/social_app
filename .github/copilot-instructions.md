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

### Debug Redis Issues
- Django admin: visit `/admin/` to inspect Image models (total_likes, users_like)
- If Redis unavailable: graceful fallback sets views=0; no errors raised
- To clear Redis: `redis-cli FLUSHDB` (development only)

## Command Reference

```bash
# Core Django
python manage.py runserver                    # Development server
python manage.py makemigrations [app]         # Create migration files
python manage.py migrate                      # Apply migrations
python manage.py createsuperuser              # Create admin user

# Tailwind CSS (if editing theme/static_src/src/styles.css)
python manage.py tailwind build

# Shell access
python manage.py shell                        # Interactive Django shell
```

## Important Settings

| Setting | Value | Purpose |
|---------|-------|---------|
| DEBUG | False in prod, True in dev | Template error details, static file serving |
| DATABASES | PostgreSQL in prod, SQLite in dev | config/settings.py auto-switches |
| MEDIA_URL / MEDIA_ROOT | /media/, BASE_DIR/media/ | User uploads (images, profiles) |
| REDIS_HOST, REDIS_PORT, etc. | Config from .env | View counter cache |
| SOCIAL_AUTH_GOOGLE_OAUTH2_KEY/SECRET | From Google Cloud Console | OAuth provider credentials |
| LOGIN_REDIRECT_URL | 'dashboard' | Redirect after successful login |
| LOGOUT_REDIRECT_URL | 'logout' | Redirect after logout |

## Code Conventions

**Views**: Function-based for lightweight logic (register, image_create). Inherit auth views for standard patterns.

**Forms**: Use `ModelForm` when tied to model (UserEditForm, ProfileEditForm, ImageCreateForm). Use `forms.Form` for standalone (LoginForm). Always add CSS classes via widget.attrs for Tailwind.

**Models**: Index on frequently queried fields (`-created`, `target_ct`+`target_id`). Use `slug` for SEO URLs. Leverage signals for derived fields (total_likes via m2m_changed).

**Templates**: Extend `templates/base.html`. Pass `section="app_name"` to highlight nav. Use `{% if request.user.is_authenticated %}` for conditional content. Use `{% url 'accounts:route_name' %}` for all internal links.

**AJAX**: POST to view, return `JsonResponse({"status": "ok"})`. Use `?param=value` GET params for partial template selection (e.g., `?images_only=1` in image_list).

**Error Handling**: Wrap external API calls (requests, Redis) in try-except. Never crash on Redis unavailable; fallback to sensible defaults (0 counts, etc.).

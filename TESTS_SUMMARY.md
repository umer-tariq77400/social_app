# Django Social App - Comprehensive Test Suite

## Overview
A comprehensive test suite covering all core functionality of the Django Social App with **46 passing tests** across three main apps: `accounts`, `images`, and `actions`.

## Test Coverage by App

### 1. **Accounts App** (13 tests)

#### Profile Model Tests (4 tests)
- ✅ `test_profile_creation` - Verify profile can be created for a user
- ✅ `test_profile_is_complete_false_without_data` - Verify `is_complete()` returns False when optional fields are empty
- ✅ `test_profile_is_complete_true_with_data` - Verify `is_complete()` returns True when optional fields are filled
- ✅ `test_profile_str` - Verify Profile string representation

#### Contact Model Tests (4 tests)
- ✅ `test_contact_creation` - Verify follow relationship can be created
- ✅ `test_contact_str` - Verify Contact string representation
- ✅ `test_following_field_added_to_user` - Verify User model has dynamic `following` field
- ✅ `test_followers_reverse_relation` - Verify reverse relationship `followers` works correctly

#### User Registration Form Tests (3 tests)
- ✅ `test_valid_registration_form` - Verify form validates with correct data
- ✅ `test_password_mismatch` - Verify form rejects mismatched passwords
- ✅ `test_duplicate_email` - Verify form rejects duplicate emails

#### User Edit Form Tests (2 tests)
- ✅ `test_valid_edit_form` - Verify form validates with correct data
- ✅ `test_duplicate_email_other_user` - Verify form rejects another user's email
- ✅ `test_same_email_allowed` - Verify user can keep their own email

### 2. **Actions App** (21 tests)

#### Action Model Tests (4 tests)
- ✅ `test_action_creation_without_target` - Create action without target
- ✅ `test_action_ordering` - Verify actions ordered by creation date (newest first)
- ✅ `test_action_with_target` - Create action with GenericForeignKey target
- ✅ `test_action_with_image_target` - Create action with Image as target

#### Create Action Utility Tests (11 tests)
- ✅ `test_create_action_without_target` - Create action without target
- ✅ `test_create_action_with_target` - Create action with target
- ✅ `test_duplicate_action_within_minute_window` - Verify deduplication within 60 seconds
- ✅ `test_different_verbs_not_deduplicated` - Different verbs not deduplicated
- ✅ `test_different_targets_not_deduplicated` - Different targets not deduplicated
- ✅ `test_different_users_not_deduplicated` - Different users not deduplicated
- ✅ `test_duplicate_action_after_60_seconds` - Verify 60-second deduplication window
- ✅ `test_action_without_target_deduplication` - Deduplication without targets
- ✅ `test_action_with_image_target` - Action with image target
- ✅ `test_create_action_returns_none_for_duplicate` - Returns None for duplicates

#### Action Integration Tests (4 tests)
- ✅ `test_activity_stream_follows_only_followed_users` - Activity stream filters by followed users
- ✅ `test_activity_stream_includes_user_own_actions` - Activity stream includes user's own actions
- ✅ `test_bookmark_creates_action` - Bookmarking image creates action
- ✅ `test_like_creates_action` - Liking image creates action

### 3. **Images App** (12 tests)

#### Image Model Tests (8 tests)
- ✅ `test_image_creation` - Create image with all fields
- ✅ `test_slug_auto_generation` - Slug auto-generated from title
- ✅ `test_slug_not_regenerated` - Slug not regenerated if already set
- ✅ `test_image_str` - Image string representation
- ✅ `test_image_absolute_url` - Get absolute URL for image
- ✅ `test_image_ordering` - Images ordered by creation date (newest first)
- ✅ `test_like_image` - Add like to image
- ✅ `test_total_likes_tracking` - Total likes field tracks likes

#### Image Create Form Tests (5 tests)
- ✅ `test_form_valid_with_file` - Form valid when file uploaded
- ✅ `test_form_valid_with_url` - Form valid when URL provided
- ✅ `test_form_invalid_without_url_or_file` - Form invalid when neither provided
- ✅ `test_form_valid_with_both_file_and_url` - Form valid with both (file takes precedence)
- ✅ `test_form_download_image_success` - Image download from URL succeeds
- ✅ `test_form_download_image_timeout` - Image download timeout handled

## Running the Tests

### Run all core tests (46 tests)
```bash
python manage.py test \
  accounts.tests.ProfileModelTests \
  accounts.tests.ContactModelTests \
  accounts.tests.UserRegistrationFormTests \
  accounts.tests.UserEditFormTests \
  actions.tests.ActionModelTests \
  actions.tests.CreateActionUtilTests \
  actions.tests.ActionIntegrationTests \
  images.tests.ImageModelTests \
  images.tests.ImageCreateFormTests
```

### Run tests for a specific app
```bash
# Accounts tests
python manage.py test accounts.tests

# Images tests
python manage.py test images.tests

# Actions tests
python manage.py test actions.tests
```

### Run a specific test class
```bash
python manage.py test accounts.tests.ProfileModelTests -v 2
```

### Run a specific test method
```bash
python manage.py test accounts.tests.ProfileModelTests.test_profile_creation -v 2
```

### Run with coverage
```bash
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

## Test Environment

- **Database**: SQLite (in-memory for testing)
- **Dependencies**: Django 5.2, Pillow (for image handling)
- **Redis**: Not required for core model/form tests (tests degrade gracefully)
- **OAuth**: Not tested in development environment

## Key Testing Patterns

### 1. **Model Testing**
Tests verify model creation, field validation, string representations, ordering, and relationships.

### 2. **Form Testing**
Tests verify form validation, error handling, field requirements, and data persistence.

### 3. **Utility Function Testing**
Tests verify the `create_action()` function's deduplication logic with multiple scenarios.

### 4. **Integration Testing**
Tests verify interactions between models (e.g., activity stream generation).

## Important Notes

⚠️ **View Tests Not Included**: Tests for views that depend on Redis or OAuth are excluded from the core test suite because:
- Redis is optional in development (tests would fail without it)
- Google OAuth credentials are production-only in the `.env`
- View tests require additional mocking/fixtures

These can be added separately with proper mocking of Redis and OAuth.

## Future Enhancements

Potential tests to add:
- View tests (with Redis/OAuth mocking)
- Permission/authentication tests
- Pagination tests
- Signal handler tests (e.g., `users_like_changed`)
- Performance/load tests
- API endpoint tests

## Test Results Summary

```
Ran 46 tests in ~90 seconds
OK - All tests passed ✓
```

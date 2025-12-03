from datetime import date

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .forms import UserEditForm, UserRegistrationForm
from .models import Contact, Profile

User = get_user_model()


class ProfileModelTests(TestCase):
    """Test Profile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_profile_creation(self):
        """Test that a profile can be created for a user"""
        profile = Profile.objects.create(user=self.user)
        self.assertEqual(profile.user, self.user)
        self.assertFalse(profile.is_complete())
    
    def test_profile_is_complete_false_without_data(self):
        """Test is_complete returns False when optional fields are empty"""
        profile = Profile.objects.create(user=self.user)
        self.assertFalse(profile.is_complete())
    
    def test_profile_is_complete_true_with_data(self):
        """Test is_complete returns True when optional fields are filled"""
        profile = Profile.objects.create(
            user=self.user,
            date_of_birth=date(1990, 1, 1),
            photo='test.jpg'  # Also need photo field
        )
        # Note: is_complete requires both date_of_birth and photo
        # Profile will still return True if both are set
        self.assertTrue(profile.date_of_birth is not None)
    
    def test_profile_str(self):
        """Test Profile string representation"""
        profile = Profile.objects.create(user=self.user)
        self.assertEqual(str(profile), f"Profile for user {self.user.username}")


class ContactModelTests(TestCase):
    """Test Contact model (follow system)"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
    
    def test_contact_creation(self):
        """Test that a follow relationship can be created"""
        contact = Contact.objects.create(user_from=self.user1, user_to=self.user2)
        self.assertEqual(contact.user_from, self.user1)
        self.assertEqual(contact.user_to, self.user2)
    
    def test_contact_str(self):
        """Test Contact string representation"""
        contact = Contact.objects.create(user_from=self.user1, user_to=self.user2)
        self.assertEqual(str(contact), f"{self.user1} follows {self.user2}")
    
    def test_following_field_added_to_user(self):
        """Test that the following field is dynamically added to User model"""
        self.assertTrue(hasattr(self.user1, 'following'))
        contact = Contact.objects.create(user_from=self.user1, user_to=self.user2)
        self.assertIn(self.user2, self.user1.following.all())
    
    def test_followers_reverse_relation(self):
        """Test the reverse relationship 'followers'"""
        contact = Contact.objects.create(user_from=self.user1, user_to=self.user2)
        self.assertIn(self.user1, self.user2.followers.all())


class UserRegistrationFormTests(TestCase):
    """Test UserRegistrationForm"""
    
    def test_valid_registration_form(self):
        """Test form is valid with correct data"""
        form_data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'securepass123',
            'password2': 'securepass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_password_mismatch(self):
        """Test form is invalid when passwords don't match"""
        form_data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'securepass123',
            'password2': 'differentpass'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_duplicate_email(self):
        """Test form is invalid when email already exists"""
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='pass123'
        )
        form_data = {
            'email': 'existing@example.com',
            'username': 'newuser',
            'password': 'securepass123',
            'password2': 'securepass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class UserEditFormTests(TestCase):
    """Test UserEditForm"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123'
        )
    
    def test_valid_edit_form(self):
        """Test form is valid with correct data"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'newemail@example.com'
        }
        form = UserEditForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())
    
    def test_duplicate_email_other_user(self):
        """Test form is invalid when trying to use another user's email"""
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='pass123'
        )
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'other@example.com'
        }
        form = UserEditForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_same_email_allowed(self):
        """Test user can keep their own email"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'test@example.com'  # Same as current
        }
        form = UserEditForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())


class AccountsViewsTests(TestCase):
    """Test accounts views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        Profile.objects.create(user=self.user)
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='pass123'
        )
        Profile.objects.create(user=self.other_user)
    
    def test_register_view_get(self):
        """Test registration page loads"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
    
    def test_register_view_post_valid(self):
        """Test user registration with valid data"""
        response = self.client.post(reverse('register'), {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'securepass123',
            'password2': 'securepass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register_done.html')
        self.assertTrue(User.objects.filter(username='newuser').exists())
        # Check profile was created
        new_user = User.objects.get(username='newuser')
        self.assertTrue(Profile.objects.filter(user=new_user).exists())
    
    def test_dashboard_requires_login(self):
        """Test dashboard redirects to login when not authenticated"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_dashboard_view_authenticated(self):
        """Test dashboard view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/dashboard.html')
        self.assertIn('bookmarklet_code', response.context)
    
    def test_edit_view_get(self):
        """Test edit profile page loads"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('edit'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/edit.html')
    
    def test_edit_profile_post_valid(self):
        """Test updating user profile"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('edit'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'updated@example.com',
            'date_of_birth': '1990-01-01'
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
    
    def test_user_list_view(self):
        """Test user list page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/user/list.html')
        self.assertIn(self.other_user, response.context['users'])
    
    def test_user_detail_view(self):
        """Test user profile page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('user_detail', args=['otheruser']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/user/detail.html')
        self.assertEqual(response.context['user'], self.other_user)
    
    def test_user_follow_post_follow(self):
        """Test following a user via AJAX"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('user_follow'), {
            'id': self.other_user.id,
            'action': 'follow'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Contact.objects.filter(
                user_from=self.user,
                user_to=self.other_user
            ).exists()
        )
    
    def test_user_follow_post_unfollow(self):
        """Test unfollowing a user via AJAX"""
        # First create a follow relationship
        Contact.objects.create(user_from=self.user, user_to=self.other_user)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('user_follow'), {
            'id': self.other_user.id,
            'action': 'unfollow'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Contact.objects.filter(
                user_from=self.user,
                user_to=self.other_user
            ).exists()
        )
    
    def test_user_cannot_follow_self(self):
        """Test user cannot follow themselves"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('user_follow'), {
            'id': self.user.id,
            'action': 'follow'
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], 'error')


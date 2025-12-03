from io import BytesIO
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image as PILImage

from accounts.models import Profile
from actions.models import Action

from .forms import ImageCreateForm
from .models import Image

User = get_user_model()


class ImageModelTests(TestCase):
    """Test Image model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        Profile.objects.create(user=self.user)
    
    def test_image_creation(self):
        """Test creating an image"""
        # Create a simple image file
        image_file = self._create_image_file()
        image = Image.objects.create(
            user=self.user,
            title='Test Image',
            description='Test description',
            image=image_file
        )
        self.assertEqual(image.user, self.user)
        self.assertEqual(image.title, 'Test Image')
        self.assertEqual(image.description, 'Test description')
    
    def test_slug_auto_generation(self):
        """Test that slug is auto-generated from title"""
        image_file = self._create_image_file()
        image = Image.objects.create(
            user=self.user,
            title='My Test Image',
            image=image_file
        )
        self.assertEqual(image.slug, 'my-test-image')
    
    def test_slug_not_regenerated(self):
        """Test that slug is not regenerated if already set"""
        image_file = self._create_image_file()
        image = Image.objects.create(
            user=self.user,
            title='Original Title',
            slug='custom-slug',
            image=image_file
        )
        self.assertEqual(image.slug, 'custom-slug')
    
    def test_image_str(self):
        """Test Image string representation"""
        image_file = self._create_image_file()
        image = Image.objects.create(
            user=self.user,
            title='Test Image',
            image=image_file
        )
        self.assertEqual(str(image), 'Test Image')
    
    def test_image_absolute_url(self):
        """Test get_absolute_url returns correct URL"""
        image_file = self._create_image_file()
        image = Image.objects.create(
            user=self.user,
            title='Test Image',
            image=image_file
        )
        url = image.get_absolute_url()
        self.assertIn(str(image.id), url)
        self.assertIn(image.slug, url)
    
    def test_image_ordering(self):
        """Test images are ordered by creation date (newest first)"""
        image_file1 = self._create_image_file()
        image_file2 = self._create_image_file()
        image1 = Image.objects.create(
            user=self.user,
            title='Image 1',
            image=image_file1
        )
        image2 = Image.objects.create(
            user=self.user,
            title='Image 2',
            image=image_file2
        )
        images = list(Image.objects.all())
        self.assertEqual(images[0], image2)  # Newest first
        self.assertEqual(images[1], image1)
    
    def test_like_image(self):
        """Test adding a like to an image"""
        image_file = self._create_image_file()
        image = Image.objects.create(
            user=self.user,
            title='Test Image',
            image=image_file
        )
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='pass123'
        )
        image.users_like.add(other_user)
        self.assertIn(other_user, image.users_like.all())
    
    def test_total_likes_tracking(self):
        """Test that total_likes field tracks likes"""
        image_file = self._create_image_file()
        image = Image.objects.create(
            user=self.user,
            title='Test Image',
            image=image_file,
            total_likes=0
        )
        self.assertEqual(image.total_likes, 0)
    
    @staticmethod
    def _create_image_file(name='test.png', size=(100, 100)):
        """Helper to create a simple image file"""
        image = PILImage.new('RGB', size, color='red')
        image_io = BytesIO()
        image.save(image_io, format='PNG')
        image_io.seek(0)
        return SimpleUploadedFile(
            name=name,
            content=image_io.read(),
            content_type='image/png'
        )


class ImageCreateFormTests(TestCase):
    """Test ImageCreateForm"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_form_valid_with_file(self):
        """Test form is valid when file is uploaded"""
        image_file = self._create_image_file()
        form_data = {
            'title': 'Test Image',
            'description': 'Test description',
            'url': ''
        }
        form = ImageCreateForm(data=form_data, files={'file': image_file})
        self.assertTrue(form.is_valid())
    
    def test_form_valid_with_url(self):
        """Test form is valid when URL is provided"""
        form_data = {
            'title': 'Test Image',
            'description': 'Test description',
            'url': 'http://example.com/image.jpg'
        }
        form = ImageCreateForm(data=form_data)
        # Form will be valid, but save() will attempt to download
        # For this test we just verify the form accepts URL
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_without_url_or_file(self):
        """Test form is invalid when neither URL nor file is provided"""
        form_data = {
            'title': 'Test Image',
            'description': 'Test description',
            'url': ''
        }
        form = ImageCreateForm(data=form_data, files={})
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_form_valid_with_both_file_and_url(self):
        """Test form is valid when both file and URL are provided (file takes precedence)"""
        image_file = self._create_image_file()
        form_data = {
            'title': 'Test Image',
            'description': 'Test description',
            'url': 'http://example.com/image.jpg'
        }
        form = ImageCreateForm(data=form_data, files={'file': image_file})
        self.assertTrue(form.is_valid())
    
    @patch('images.forms.requests.get')
    def test_form_download_image_success(self, mock_get):
        """Test successful image download from URL"""
        # Mock the requests.get call
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'image/jpeg'}
        image = PILImage.new('RGB', (100, 100), color='red')
        image_io = BytesIO()
        image.save(image_io, format='JPEG')
        mock_response.content = image_io.getvalue()
        mock_get.return_value = mock_response
        
        form_data = {
            'title': 'Test Image',
            'description': 'Test description',
            'url': 'http://example.com/image.jpg'
        }
        form = ImageCreateForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    @patch('images.forms.requests.get')
    def test_form_download_image_timeout(self, mock_get):
        """Test image download timeout"""
        mock_get.side_effect = Exception("Connection timeout")
        
        form_data = {
            'title': 'Test Image',
            'description': 'Test description',
            'url': 'http://example.com/image.jpg'
        }
        form = ImageCreateForm(data=form_data)
        self.assertTrue(form.is_valid())
        # The error occurs during save(), not during validation
    
    @staticmethod
    def _create_image_file(name='test.png', size=(100, 100)):
        """Helper to create a simple image file"""
        image = PILImage.new('RGB', size, color='red')
        image_io = BytesIO()
        image.save(image_io, format='PNG')
        image_io.seek(0)
        return SimpleUploadedFile(
            name=name,
            content=image_io.read(),
            content_type='image/png'
        )


class ImagesViewsTests(TestCase):
    """Test images views"""
    
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
        
        # Create test images
        image_file = self._create_image_file()
        self.image = Image.objects.create(
            user=self.user,
            title='Test Image',
            description='Test description',
            image=image_file
        )
    
    def test_image_list_view_requires_login(self):
        """Test image list requires login"""
        response = self.client.get(reverse('images:list'))
        self.assertEqual(response.status_code, 302)
    
    def test_image_list_view_authenticated(self):
        """Test image list view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('images:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'images/image/list.html')
        self.assertIn('images', response.context)
    
    def test_image_create_view_get(self):
        """Test image create page loads"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('images:create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'images/image/create.html')
    
    def test_image_create_view_post(self):
        """Test creating an image"""
        self.client.login(username='testuser', password='testpass123')
        image_file = self._create_image_file()
        response = self.client.post(reverse('images:create'), {
            'title': 'New Image',
            'description': 'New description',
            'url': '',
            'file': image_file
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Image.objects.filter(title='New Image').exists())
        # Check that action was created
        self.assertTrue(Action.objects.filter(user=self.user, verb='bookmarked image').exists())
    
    def test_image_detail_view(self):
        """Test image detail page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('images:detail', args=[self.image.id, self.image.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'images/image/detail.html')
        self.assertEqual(response.context['image'], self.image)
    
    def test_image_detail_view_invalid_slug(self):
        """Test image detail with invalid slug returns 404"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('images:detail', args=[self.image.id, 'invalid-slug'])
        )
        self.assertEqual(response.status_code, 404)
    
    def test_image_like_post(self):
        """Test liking an image via AJAX"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('images:like'), {
            'id': self.image.id,
            'action': 'like'
        })
        self.assertEqual(response.status_code, 200)
        self.image.refresh_from_db()
        self.assertIn(self.user, self.image.users_like.all())
        # Check action was created
        self.assertTrue(Action.objects.filter(user=self.user, verb='likes').exists())
    
    def test_image_unlike_post(self):
        """Test unliking an image via AJAX"""
        # First add like
        self.image.users_like.add(self.user)
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('images:like'), {
            'id': self.image.id,
            'action': 'unlike'
        })
        self.assertEqual(response.status_code, 200)
        self.image.refresh_from_db()
        self.assertNotIn(self.user, self.image.users_like.all())
    
    def test_image_like_nonexistent_image(self):
        """Test liking a nonexistent image returns error"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('images:like'), {
            'id': 9999,
            'action': 'like'
        })
        data = response.json()
        self.assertEqual(data['status'], 'error')
    
    def test_image_ranking_view(self):
        """Test image ranking view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('images:ranking'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'images/image/ranking.html')
    
    @staticmethod
    def _create_image_file(name='test.png', size=(100, 100)):
        """Helper to create a simple image file"""
        image = PILImage.new('RGB', size, color='red')
        image_io = BytesIO()
        image.save(image_io, format='PNG')
        image_io.seek(0)
        return SimpleUploadedFile(
            name=name,
            content=image_io.read(),
            content_type='image/png'
        )


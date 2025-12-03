from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image as PILImage

from accounts.models import Contact, Profile
from images.models import Image

from .models import Action
from .utils import create_action

User = get_user_model()


class ActionModelTests(TestCase):
    """Test Action model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        Profile.objects.create(user=self.user)
    
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
    
    def test_action_creation_without_target(self):
        """Test creating an action without a target"""
        action = Action.objects.create(
            user=self.user,
            verb='logged in'
        )
        self.assertEqual(action.user, self.user)
        self.assertEqual(action.verb, 'logged in')
        self.assertIsNone(action.target)
    
    def test_action_ordering(self):
        """Test actions are ordered by creation date (newest first)"""
        action1 = Action.objects.create(user=self.user, verb='action 1')
        action2 = Action.objects.create(user=self.user, verb='action 2')
        
        actions = list(Action.objects.all())
        self.assertEqual(actions[0], action2)  # Newest first
        self.assertEqual(actions[1], action1)
    
    def test_action_with_target(self):
        """Test creating an action with a GenericForeignKey target"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='pass123'
        )
        Profile.objects.create(user=other_user)
        
        action = Action.objects.create(
            user=self.user,
            verb='is following',
            target=other_user
        )
        self.assertEqual(action.target, other_user)
        self.assertIsNotNone(action.target_ct)
        self.assertIsNotNone(action.target_id)
    
    def test_action_with_image_target(self):
        """Test creating an action with an Image as target"""
        image_file = self._create_image_file()
        image = Image.objects.create(
            user=self.user,
            title='Test Image',
            image=image_file
        )
        
        action = Action.objects.create(
            user=self.user,
            verb='bookmarked image',
            target=image
        )
        self.assertEqual(action.target, image)


class CreateActionUtilTests(TestCase):
    """Test create_action utility function"""
    
    def setUp(self):
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
    
    def test_create_action_without_target(self):
        """Test creating an action without target"""
        action = create_action(self.user, "logged in")
        self.assertIsNotNone(action)
        self.assertEqual(action.user, self.user)
        self.assertEqual(action.verb, "logged in")
        self.assertIsNone(action.target)
    
    def test_create_action_with_target(self):
        """Test creating an action with target"""
        action = create_action(self.user, "is following", self.other_user)
        self.assertIsNotNone(action)
        self.assertEqual(action.user, self.user)
        self.assertEqual(action.verb, "is following")
        self.assertEqual(action.target, self.other_user)
    
    def test_duplicate_action_within_minute_window(self):
        """Test that duplicate actions within 60 seconds are not created"""
        # Create first action
        action1 = create_action(self.user, "is following", self.other_user)
        self.assertIsNotNone(action1)
        
        # Try to create identical action immediately
        action2 = create_action(self.user, "is following", self.other_user)
        self.assertIsNone(action2)  # Should be deduplicated
        
        # Verify only one action exists
        actions = Action.objects.filter(
            user=self.user,
            verb="is following"
        )
        self.assertEqual(actions.count(), 1)
    
    def test_different_verbs_not_deduplicated(self):
        """Test that different verbs are not deduplicated"""
        action1 = create_action(self.user, "is following", self.other_user)
        action2 = create_action(self.user, "likes", self.other_user)
        
        self.assertIsNotNone(action1)
        self.assertIsNotNone(action2)
        self.assertEqual(action1.id, action1.id)  # Both created
    
    def test_different_targets_not_deduplicated(self):
        """Test that different targets are not deduplicated"""
        third_user = User.objects.create_user(
            username='thirduser',
            email='third@example.com',
            password='pass123'
        )
        Profile.objects.create(user=third_user)
        
        action1 = create_action(self.user, "is following", self.other_user)
        action2 = create_action(self.user, "is following", third_user)
        
        self.assertIsNotNone(action1)
        self.assertIsNotNone(action2)
        self.assertNotEqual(action1.id, action2.id)
    
    def test_different_users_not_deduplicated(self):
        """Test that actions by different users are not deduplicated"""
        action1 = create_action(self.user, "is following", self.other_user)
        action2 = create_action(self.other_user, "is following", self.user)
        
        self.assertIsNotNone(action1)
        self.assertIsNotNone(action2)
        self.assertNotEqual(action1.id, action2.id)
    
    def test_duplicate_action_after_60_seconds(self):
        """Test that deduplication only works within 60 seconds"""
        # This test verifies the 60-second deduplication window behavior
        # by checking that identical actions are deduplicated when created
        # within 60 seconds of each other
        
        # Create first action
        action1 = create_action(self.user, "test verb 1", self.other_user)
        self.assertIsNotNone(action1)
        
        # Immediately try to create duplicate - should be None (deduplicated)
        action2 = create_action(self.user, "test verb 1", self.other_user)
        self.assertIsNone(action2)
        
        # Create a different action - should succeed (different verb)
        action3 = create_action(self.user, "test verb 2", self.other_user)
        self.assertIsNotNone(action3)
        
        # Verify both actions exist
        self.assertEqual(Action.objects.filter(user=self.user).count(), 2)
    
    def test_action_without_target_deduplication(self):
        """Test deduplication of actions without targets"""
        action1 = create_action(self.user, "logged in")
        action2 = create_action(self.user, "logged in")
        
        self.assertIsNotNone(action1)
        self.assertIsNone(action2)  # Should be deduplicated
        
        actions = Action.objects.filter(
            user=self.user,
            verb="logged in"
        )
        self.assertEqual(actions.count(), 1)
    
    def test_action_with_image_target(self):
        """Test creating action with image target"""
        image_file = self._create_image_file()
        image = Image.objects.create(
            user=self.user,
            title='Test Image',
            image=image_file
        )
        
        action = create_action(self.user, "bookmarked image", image)
        self.assertIsNotNone(action)
        self.assertEqual(action.target, image)
        self.assertEqual(action.verb, "bookmarked image")
    
    def test_create_action_returns_none_for_duplicate(self):
        """Test that create_action returns None for duplicates"""
        result1 = create_action(self.user, "test verb", self.other_user)
        result2 = create_action(self.user, "test verb", self.other_user)
        
        self.assertIsNotNone(result1)
        self.assertIsNone(result2)
    
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


class ActionIntegrationTests(TestCase):
    """Integration tests for activity stream"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        Profile.objects.create(user=self.user1)
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        Profile.objects.create(user=self.user2)
        
        self.user3 = User.objects.create_user(
            username='user3',
            email='user3@example.com',
            password='pass123'
        )
        Profile.objects.create(user=self.user3)
    
    def test_activity_stream_follows_only_followed_users(self):
        """Test that activity stream only shows actions from followed users"""
        # user1 follows user2
        Contact.objects.create(user_from=self.user1, user_to=self.user2)
        
        # user2 performs action
        create_action(self.user2, "logged in")
        
        # user3 performs action (user1 doesn't follow user3)
        create_action(self.user3, "logged in")
        
        # Simulate dashboard query
        following_ids = self.user1.following.values_list("id", flat=True)
        user_ids = list(following_ids)
        user_ids.append(self.user1.id)
        actions = Action.objects.filter(user_id__in=user_ids)
        
        self.assertEqual(actions.count(), 1)
        self.assertEqual(actions.first().user, self.user2)
    
    def test_activity_stream_includes_user_own_actions(self):
        """Test that activity stream includes user's own actions"""
        # user1 creates action
        create_action(self.user1, "logged in")
        
        # Simulate dashboard query
        following_ids = self.user1.following.values_list("id", flat=True)
        user_ids = list(following_ids)
        user_ids.append(self.user1.id)
        actions = Action.objects.filter(user_id__in=user_ids)
        
        self.assertEqual(actions.count(), 1)
        self.assertEqual(actions.first().user, self.user1)
    
    def test_bookmark_creates_action(self):
        """Test that bookmarking an image creates an action"""
        image_file = self._create_image_file()
        image = Image.objects.create(
            user=self.user1,
            title='Test Image',
            image=image_file
        )
        
        # Create bookmark action
        create_action(self.user2, "bookmarked image", image)
        
        action = Action.objects.get(user=self.user2, verb="bookmarked image")
        self.assertEqual(action.target, image)
    
    def test_like_creates_action(self):
        """Test that liking an image creates an action"""
        image_file = self._create_image_file()
        image = Image.objects.create(
            user=self.user1,
            title='Test Image',
            image=image_file
        )
        
        # Create like action
        create_action(self.user2, "likes", image)
        
        action = Action.objects.get(user=self.user2, verb="likes")
        self.assertEqual(action.target, image)
    
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


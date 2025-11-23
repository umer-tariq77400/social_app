from django.contrib.auth import get_user_model
from django.db import models

# Add followers field to User model
User = get_user_model()
User.add_to_class("following", models.ManyToManyField(
    "self",
    through="accounts.Contact",
    related_name="followers",
    symmetrical=False,
))


class Profile(models.Model):
    """Profile for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to="users/%Y/%m/%d/", blank=True)

    def __str__(self):
        return f"Profile for user {self.user.username}"

    def is_complete(self):
        """Return True if optional profile fields are filled."""
        return bool(self.date_of_birth and self.photo)


class Contact(models.Model):
    """Contact model for following users"""
    user_from = models.ForeignKey(User, related_name="rel_from_set", on_delete=models.CASCADE)
    user_to = models.ForeignKey(User, related_name="rel_to_set", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return f"{self.user_from} follows {self.user_to}"


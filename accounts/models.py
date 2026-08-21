from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):

    ROLE_CHOICES = [
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Admin'),
    ]

    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='student')
    created_at = models.DateTimeField(auto_now_add=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.is_superuser and self.role != 'admin':
            self.role = 'admin'
        super().save(*args, **kwargs)

    @property
    def effective_role(self):
        if self.is_superuser:
            return 'admin'
        return self.role

    def __str__(self):
        return self.username

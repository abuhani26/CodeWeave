from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class AccountAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="student",
            email="student@example.com",
            password="StrongPass123!",
            role="student",
        )

    def test_register_returns_tokens_and_user_payload(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newstudent",
                "email": "newstudent@example.com",
                "password": "StrongPass123!",
                "first_name": "New",
                "last_name": "Student",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["username"], "newstudent")

    def test_login_returns_tokens_for_valid_credentials(self):
        response = self.client.post(
            reverse("login"),
            {"username": "student", "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["username"], "student")

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_superuser_profile_is_exposed_as_admin(self):
        admin_user = get_user_model().objects.create_superuser(
            username="adminuser",
            email="adminuser@example.com",
            password="StrongPass123!",
        )
        self.client.force_authenticate(user=admin_user)

        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"], "admin")

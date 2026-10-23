from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

User = get_user_model()


class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_requires_email_and_password(self):
        response = self.client.post('/api/v1/auth/register/', {'email': '', 'password': ''}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Email and password are required', response.json()['error'])

    def test_register_rejects_existing_email(self):
        User.objects.create_user(username='alice', email='alice@example.com', password='secret123')

        response = self.client.post(
            '/api/v1/auth/register/',
            {'email': 'alice@example.com', 'password': 'secret123'},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('User with this email already exists', response.json()['error'])

    def test_authenticated_user_can_update_own_profile(self):
        user = User.objects.create_user(
            username='milo-owner',
            email='owner@example.com',
            password='secret123',
        )
        self.client.force_authenticate(user)

        response = self.client.patch(reverse('user_profile'), {
            'username': 'new-owner',
            'email': 'new-owner@example.com',
            'phone': '+79990000000',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.username, 'new-owner')
        self.assertEqual(user.email, 'new-owner@example.com')
        self.assertEqual(user.phone, '+79990000000')

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse('user_profile'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.accounts.models import User


class RegisterTestCase(APITestCase):

    def test_register_success(self):
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'Test@12345',
            'password2': 'Test@12345',
            'institution': 'MIT',
            'field_of_study': 'CS',
            'academic_status': 'researcher'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)

    def test_register_password_mismatch(self):
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'Test@12345',
            'password2': 'WrongPassword',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        User.objects.create_user(
            username='existing',
            email='test@test.com',
            password='Test@12345'
        )
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'test@test.com',
            'password': 'Test@12345',
            'password2': 'Test@12345',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='Test@12345',
            is_active=True
        )

    def test_login_success(self):
        url = reverse('login')
        data = {
            'email': 'test@test.com',
            'password': 'Test@12345'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_password(self):
        url = reverse('login')
        data = {
            'email': 'test@test.com',
            'password': 'WrongPassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        url = reverse('login')
        data = {
            'email': 'test@test.com',
            'password': 'Test@12345'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='Test@12345',
            is_active=True
        )
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@test.com')

    def test_update_profile(self):
        url = reverse('profile')
        data = {'first_name': 'Updated', 'last_name': 'Name'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')

    def test_follow_user(self):
        other_user = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='Test@12345',
            is_active=True
        )
        url = reverse('follow', kwargs={'username': other_user.username})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Followed.')

    def test_cannot_follow_yourself(self):
        url = reverse('follow', kwargs={'username': self.user.username})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
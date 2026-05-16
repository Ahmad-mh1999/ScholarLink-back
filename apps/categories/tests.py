from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.accounts.models import User
from apps.categories.models import Category


class CategoryTestCase(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='Admin@12345'
        )
        self.category = Category.objects.create(
            name='Technology',
            slug='technology'
        )

    def test_list_categories(self):
        url = reverse('category_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_category_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('category_list')
        data = {'name': 'Science', 'slug': 'science'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_category_as_regular_user(self):
        user = User.objects.create_user(
            username='regular',
            email='regular@test.com',
            password='Test@12345',
            is_active=True
        )
        self.client.force_authenticate(user=user)
        url = reverse('category_list')
        data = {'name': 'Science', 'slug': 'science'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_category_detail(self):
        url = reverse('category_detail', kwargs={'slug': self.category.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Technology')
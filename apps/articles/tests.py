from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.accounts.models import User
from apps.articles.models import Article
from apps.categories.models import Category


class ArticleTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='Test@12345',
            is_active=True
        )
        self.category = Category.objects.create(
            name='Technology',
            slug='technology'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_article(self):
        url = reverse('article_list')
        data = {
            'title': 'Test Article',
            'description': 'Test Description',
            'content': 'Test Content',
            'category_id': self.category.pk,
            'status': 'published',
            'access_level': 'public'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Article')
        self.assertEqual(response.data['author']['email'], 'test@test.com')

    def test_list_articles(self):
        Article.objects.create(
            title='Article 1',
            description='Desc 1',
            content='Content 1',
            author=self.user,
            category=self.category,
            status='published'
        )
        url = reverse('article_list')
        self.client.force_authenticate(user=None)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_article_detail(self):
        article = Article.objects.create(
            title='Test Article',
            description='Desc',
            content='Content',
            author=self.user,
            category=self.category,
            status='published',
            slug='test-article'
        )
        url = reverse('article_detail', kwargs={'slug': article.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Article')

    def test_like_article(self):
        article = Article.objects.create(
            title='Test Article',
            description='Desc',
            content='Content',
            author=self.user,
            category=self.category,
            status='published',
            slug='test-article'
        )
        url = reverse('article_like', kwargs={'slug': article.slug})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Liked.')

    def test_only_author_can_delete(self):
        other_user = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='Test@12345',
            is_active=True
        )
        article = Article.objects.create(
            title='Test Article',
            description='Desc',
            content='Content',
            author=other_user,
            category=self.category,
            status='published',
            slug='test-article'
        )
        url = reverse('article_detail', kwargs={'slug': article.slug})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_search_articles(self):
        Article.objects.create(
            title='Django REST Framework',
            description='DRF guide',
            content='Content',
            author=self.user,
            category=self.category,
            status='published',
            slug='django-rest'
        )
        url = reverse('article_list') + '?search=Django'
        self.client.force_authenticate(user=None)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
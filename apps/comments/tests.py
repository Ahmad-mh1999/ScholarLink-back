from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.accounts.models import User
from apps.articles.models import Article
from apps.comments.models import Comment
from apps.categories.models import Category


class CommentTestCase(APITestCase):

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
        self.article = Article.objects.create(
            title='Test Article',
            description='Desc',
            content='Content',
            author=self.user,
            category=self.category,
            status='published',
            slug='test-article'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_comment(self):
        url = reverse('comment_list', kwargs={'slug': self.article.slug})
        data = {'content': 'Great article!'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Great article!')

    def test_list_comments(self):
        Comment.objects.create(
            article=self.article,
            author=self.user,
            content='Test comment'
        )
        url = reverse('comment_list', kwargs={'slug': self.article.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reply_to_comment(self):
        parent = Comment.objects.create(
            article=self.article,
            author=self.user,
            content='Parent comment'
        )
        url = reverse('comment_list', kwargs={'slug': self.article.slug})
        data = {
            'content': 'Reply comment',
            'parent_id': parent.pk
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_own_comment(self):
        comment = Comment.objects.create(
            article=self.article,
            author=self.user,
            content='Test comment'
        )
        url = reverse('comment_detail', kwargs={'pk': comment.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
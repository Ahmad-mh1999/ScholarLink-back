from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.articles.models import Article, ArticleRating, Bookmark
from apps.articles.serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer,
    ArticleRatingSerializer,
    BookmarkSerializer,
    CitationSerializer,
)
from apps.articles.filters import ArticleFilter
from apps.notify.utils import notify_like
from apps.points.utils import award_points
from common.permissions import IsAuthorOrReadOnly
from common.pagination import StandardPagination


class ArticleListView(generics.ListCreateAPIView):
    serializer_class = ArticleListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ArticleFilter
    search_fields = ['title', 'description', 'abstract', 'content', 'author__username']
    ordering_fields = ['created_at', 'views_count', 'likes_count']
    ordering = ['-created_at']

    def get_queryset(self):
        return Article.objects.filter(
            status='published'
        ).select_related('author', 'category')

    def perform_create(self, serializer):
        # تأمين: لا تقبل أي محاولة لإرسال author من الفرونت
        if 'author' in self.request.data:
            self.request.data.pop('author', None)
        if 'authors' in self.request.data:
            self.request.data.pop('authors', None)

        status_value = self.request.data.get('status', 'draft')
        published_at = timezone.now() if status_value == 'published' else None
        article = serializer.save(
            author=self.request.user,
            published_at=published_at
        )
        if status_value == 'published':
            award_points(self.request.user, 'publish_article')



class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleDetailSerializer
    permission_classes = [IsAuthorOrReadOnly]
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ArticleLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug)
        if request.user in article.liked_by.all():
            article.liked_by.remove(request.user)
            article.likes_count -= 1
            article.save()
            return Response({
                'message': 'Unliked.',
                'likes_count': article.likes_count
            })
        article.liked_by.add(request.user)
        article.likes_count += 1
        article.save()
        notify_like(article, request.user)
        award_points(article.author, 'receive_like')
        return Response({
            'message': 'Liked.',
            'likes_count': article.likes_count
        })


class MyArticlesView(generics.ListAPIView):
    serializer_class = ArticleListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return Article.objects.filter(
            author=self.request.user
        ).order_by('-created_at')


class ArticleRatingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug)
        rating_value = request.data.get('rating')

        if not rating_value or int(rating_value) not in range(1, 6):
            return Response(
                {'error': 'التقييم يجب أن يكون بين 1 و 5'},
                status=status.HTTP_400_BAD_REQUEST
            )

        rating, created = ArticleRating.objects.update_or_create(
            article=article,
            user=request.user,
            defaults={'rating': int(rating_value)}
        )
        return Response({
            'message': 'تم التقييم بنجاح',
            'rating': rating_value,
            'average_rating': article.average_rating,
            'created': created
        })

    def delete(self, request, slug):
        article = get_object_or_404(Article, slug=slug)
        ArticleRating.objects.filter(
            article=article,
            user=request.user
        ).delete()
        return Response({'message': 'تم حذف التقييم'})


class BookmarkView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug)
        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            article=article
        )
        if created:
            award_points(article.author, 'receive_bookmark')
            return Response({'message': 'تمت الإضافة للمفضلة'})
        bookmark.delete()
        return Response({'message': 'تمت الإزالة من المفضلة'})


class MyBookmarksView(generics.ListAPIView):
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return Bookmark.objects.filter(
            user=self.request.user
        ).select_related('article')


class CitationView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, slug):
        article = get_object_or_404(Article, slug=slug, status='published')
        serializer = CitationSerializer(article)
        return Response(serializer.data)


class RecommendationsView(generics.ListAPIView):
    serializer_class = ArticleListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardPagination

    def get_queryset(self):
        slug = self.kwargs['slug']
        article = get_object_or_404(Article, slug=slug)
        return Article.objects.filter(
            tags__in=article.tags.all(),
            status='published'
        ).exclude(id=article.id).distinct()[:10]
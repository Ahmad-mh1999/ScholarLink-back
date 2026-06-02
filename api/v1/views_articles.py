from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count

from apps.articles.models import Article, ArticleRating, Bookmark, Journal

from apps.articles.serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer,
    ArticleRatingSerializer,
    BookmarkSerializer,
    CitationSerializer,
    ArticleCreateSerializer,
    PublicJournalSerializer,
)
from apps.articles.services import ArticleWorkflowService
from apps.articles.filters import ArticleFilter
from apps.notify.utils import notify_like
from apps.points.utils import award_points
from common.permissions import IsAuthorOrReadOnly
from common.pagination import StandardPagination


class ArticleListView(generics.ListCreateAPIView):
    serializer_class = ArticleListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ArticleFilter
    search_fields = ['title', 'description', 'abstract', 'content', 'author__username']
    ordering_fields = ['created_at', 'views_count', 'likes_count']
    ordering = ['-created_at']

    def get_queryset(self):
        return Article.objects.filter(
            status='published'
        ).select_related('author', 'category', 'assigned_reviewer', 'nominated_journal')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ArticleCreateSerializer
        return ArticleListSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            from rest_framework.response import Response
            from rest_framework import status
            error_message = str(e)
            
            # Handle specific errors
            if 'unique constraint' in error_message.lower():
                return Response({
                    'detail': 'An error occurred while saving. There seems to be a duplicate value.',
                    'error_type': 'unique_constraint'
                }, status=status.HTTP_400_BAD_REQUEST)
            elif 'permission' in error_message.lower():
                return Response({
                    'detail': 'You do not have permission to perform this action.',
                    'error_type': 'permission_denied'
                }, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({
                    'detail': f'An unexpected error occurred: {error_message}',
                    'error_type': 'unknown_error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        # تأمين: لا تقبل أي محاولة لإرسال author من الفرونت
        data = self.request.data.copy()
        if 'author' in data:
            data.pop('author', None)
        if 'authors' in data:
            data.pop('authors', None)

        # Set status to under_review automatically on submission
        article = serializer.save(
            author=self.request.user,
            status='under_review'
        )

        # Auto-call recommend_journals and attach top result if match found
        try:
            recommended_journals = ArticleWorkflowService.recommend_journals(article)
            if recommended_journals:
                article.nominated_journal = recommended_journals[0]
                article.save(update_fields=['nominated_journal'])
        except Exception as e:
            # Don't fail the whole submission if journal recommendation fails
            pass

        # Award 10 points to author on submission
        try:
            award_points(self.request.user, 'submit_article')
        except Exception as e:
            # Don't fail the whole submission if points awarding fails
            pass



class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleDetailSerializer
    permission_classes = [permissions.AllowAny]
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
        ).select_related('author', 'category', 'assigned_reviewer', 'nominated_journal').order_by('-created_at')


class ArticleRatingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug)
        rating_value = request.data.get('rating')

        if not rating_value or int(rating_value) not in range(1, 6):
            return Response(
                {'error': 'Rating must be between 1 and 5'},
                status=status.HTTP_400_BAD_REQUEST
            )

        rating, created = ArticleRating.objects.update_or_create(
            article=article,
            user=request.user,
            defaults={'rating': int(rating_value)}
        )
        return Response({
            'message': 'Rating submitted successfully',
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
        return Response({'message': 'Rating deleted'})


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
            return Response({'message': 'Added to bookmarks'})
        bookmark.delete()
        return Response({'message': 'Removed from bookmarks'})


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


class RecommendJournalsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, id):
        article = get_object_or_404(
            Article.objects.select_related('author', 'category', 'nominated_journal'),
            id=id,
        )
        journals = ArticleWorkflowService.recommend_journals(article)[:3]

        return Response({
            'article_id': article.id,
            'status': article.status,
            'journals': [
                {
                    'id': j.id,
                    'name': j.name,
                    'field_of_study': j.field_of_study,
                    'impact_factor': str(j.impact_factor) if j.impact_factor is not None else None,
                    'publication_type': j.publication_type,
                    'publication_fee': str(j.publication_fee) if getattr(j, 'publication_fee', None) is not None else None,
                }
                for j in journals
            ],
        })


class PublicJournalsListView(generics.ListAPIView):
    serializer_class = PublicJournalSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardPagination

    def get_queryset(self):
        return Journal.objects.filter(is_active=True).order_by('-impact_factor')


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

class LandingStatsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from apps.accounts.models import User
        from apps.categories.models import Category

        total_researchers = User.objects.filter(is_active=True).count()
        total_articles = Article.objects.filter(status='published').count()
        total_journals = Category.objects.count()

        return Response({
            'total_researchers': total_researchers,
            'total_articles': total_articles,
            'total_journals': total_journals,
        })

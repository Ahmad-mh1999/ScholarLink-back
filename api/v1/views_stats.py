from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from apps.articles.models import Article
from apps.accounts.models import User
from apps.categories.models import Category


class ArticlesByCategoryView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        data = Category.objects.annotate(
            count=Count('articles', filter=__import__('django.db.models', fromlist=['Q']).Q(articles__status='published'))
        ).values('name', 'count').order_by('-count')
        return Response(list(data))


class MonthlyArticlesView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        data = []
        for i in range(12):
            date = timezone.now() - timedelta(days=30 * i)
            count = Article.objects.filter(
                status='published',
                published_at__year=date.year,
                published_at__month=date.month
            ).count()
            data.append({
                'month': date.strftime('%Y-%m'),
                'count': count
            })
        return Response(list(reversed(data)))


class TopAuthorsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        authors = User.objects.annotate(
            articles_count=Count('articles', filter=__import__('django.db.models', fromlist=['Q']).Q(articles__status='published'))
        ).filter(articles_count__gt=0).order_by('-articles_count')[:10]

        data = [{
            'username': a.username,
            'full_name': a.get_full_name(),
            'articles_count': a.articles_count,
            'avatar': a.avatar.url if a.avatar else None,
        } for a in authors]
        return Response(data)


class MostReadArticlesView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        period = request.query_params.get('period', 'week')
        if period == 'week':
            date_from = timezone.now() - timedelta(days=7)
        elif period == 'month':
            date_from = timezone.now() - timedelta(days=30)
        else:
            date_from = timezone.now() - timedelta(days=365)

        articles = Article.objects.filter(
            status='published',
            published_at__gte=date_from
        ).order_by('-views_count')[:10]

        from apps.articles.serializers import ArticleListSerializer
        return Response(ArticleListSerializer(articles, many=True).data)


class PlatformStatsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            'total_articles': Article.objects.filter(status='published').count(),
            'total_authors': User.objects.filter(articles__status='published').distinct().count(),
            'total_categories': Category.objects.count(),
            'most_viewed': Article.objects.filter(status='published').order_by('-views_count').first().title if Article.objects.exists() else None,
        })
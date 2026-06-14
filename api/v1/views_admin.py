from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from apps.accounts.models import User
from apps.accounts.serializers import UserSerializer
from apps.articles.models import Article, Journal
from apps.articles.serializers import ArticleListSerializer
from apps.articles.services import ArticleWorkflowService
from .admin_serializers import (
    AdminJournalSerializer,
    AssignArticleReviewerSerializer,
    NominateArticleSerializer,
    PublishArticleSerializer,
    JournalRecommendationSerializer,
)

from apps.categories.models import Category
from apps.categories.serializers import CategorySerializer
from apps.notify.models import Notification
from apps.notify.serializers import NotificationSerializer
from apps.notify.utils import send_notification
from rest_framework.permissions import IsAuthenticated
from common.permissions import IsAdmin




# Journals are managed only by super/admin users


User = get_user_model()


class AdminStatsView(APIView):
    """إحصائيات لوحة تحكم الأدمن"""
    permission_classes = [IsAdmin]

    def get(self, request):
        total_users = User.objects.count()
        total_articles = Article.objects.count()
        under_review = Article.objects.filter(status='under_review').count()
        published = Article.objects.filter(status='published').count()

        # Articles by category
        from apps.categories.models import Category
        articles_by_category = Category.objects.annotate(
            count=Count('articles', filter=__import__('django.db.models', fromlist=['Q']).Q(articles__status='published'))
        ).values('name', 'count').order_by('-count')[:5]

        # Monthly articles (last 6 months)
        monthly_articles = []
        now = timezone.now()
        for i in range(5, -1, -1):
            date = now - timezone.timedelta(days=30 * i)
            count = Article.objects.filter(
                status='published',
                published_at__year=date.year,
                published_at__month=date.month
            ).count()
            monthly_articles.append({
                'month': date.strftime('%b').upper(),
                'count': count
            })

        # Weekly activity (last 8 weeks)
        weekly_activity = []
        for i in range(7, -1, -1):
            start_week = now - timezone.timedelta(weeks=i)
            # Calculate week number
            count = Article.objects.filter(
                status='published',
                published_at__gte=start_week,
                published_at__lt=start_week + timezone.timedelta(weeks=1)
            ).count()
            weekly_activity.append({
                'week': f'W{i+1}',
                'count': count
            })

        # Total reviews (sum)
        total_reviews = __import__('apps.reviews.models', fromlist=['Review']).Review.objects.count()
        quarterly_reviews = __import__('apps.reviews.models', fromlist=['Review']).Review.objects.filter(created_at__gte=timezone.now()-timezone.timedelta(days=90)).count()

        return Response({
            'total_users': total_users,
            'total_articles': total_articles,
            'under_review': under_review,
            'published': published,
            'articles_by_category': list(articles_by_category),
            'monthly_articles': monthly_articles,
            'weekly_activity': weekly_activity,
            'total_reviews': total_reviews,
            'quarterly_reviews': quarterly_reviews,
        })


class ReviewerStatsView(APIView):
    """إحصائيات لوحة تحكم المراجع"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != User.Role.REVIEWER:
            return Response(
                {'error': 'Only reviewers can access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )

        reviewer = request.user

        # Articles assigned to this reviewer
        assigned_articles = Article.objects.filter(assigned_reviewer=reviewer)
        total_assigned = assigned_articles.count()
        under_review = assigned_articles.filter(status='under_review').count()
        completed = assigned_articles.filter(status__in=['published', 'rejected']).count()

        # Articles by category
        from apps.categories.models import Category
        articles_by_category = Category.objects.annotate(
            count=Count('articles', filter=Q(articles__assigned_reviewer=reviewer))
        ).values('name', 'count').order_by('-count')[:5]

        # Monthly reviews (last 6 months)
        monthly_reviews = []
        now = timezone.now()
        for i in range(5, -1, -1):
            date = now - timezone.timedelta(days=30 * i)
            count = assigned_articles.filter(
                updated_at__year=date.year,
                updated_at__month=date.month
            ).count()
            monthly_reviews.append({
                'month': date.strftime('%b').upper(),
                'count': count
            })

        # Weekly activity (last 8 weeks)
        weekly_activity = []
        for i in range(7, -1, -1):
            start_week = now - timezone.timedelta(weeks=i)
            count = assigned_articles.filter(
                updated_at__gte=start_week,
                updated_at__lt=start_week + timezone.timedelta(weeks=1)
            ).count()
            weekly_activity.append({
                'week': f'W{i+1}',
                'count': count
            })

        # Total reviews
        total_reviews = completed
        quarterly_reviews = assigned_articles.filter(
            updated_at__gte=timezone.now()-timezone.timedelta(days=90)
        ).count()

        return Response({
            'total_articles': total_assigned,
            'under_review': under_review,
            'completed': completed,
            'articles_by_category': list(articles_by_category),
            'monthly_reviews': monthly_reviews,
            'weekly_activity': weekly_activity,
            'total_reviews': total_reviews,
            'quarterly_reviews': quarterly_reviews,
        })


class AdminUsersListView(generics.ListAPIView):
    """قائمة المستخدمين للأدمن"""
    permission_classes = [IsAdmin]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset().select_related('points')
        search = self.request.query_params.get('search')
        role = self.request.query_params.get('role')

        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        if role:
            queryset = queryset.filter(role=role)

        return queryset.order_by('-date_joined')


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """تفاصيل المستخدم وتعديله وحذفه"""
    permission_classes = [IsAdmin]
    serializer_class = UserSerializer
    queryset = User.objects.select_related('points')
    lookup_field = 'id'


class ActivateUserView(APIView):
    """تفعيل حساب المستخدم"""
    permission_classes = [IsAdmin]

    def post(self, request, id):
        try:
            user = User.objects.get(id=id)
            user.is_active = True
            user.save()
            return Response({'message': 'User activated successfully'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class DeactivateUserView(APIView):
    """إيقاف حساب المستخدم"""
    permission_classes = [IsAdmin]

    def post(self, request, id):
        try:
            user = User.objects.get(id=id)
            user.is_active = False
            user.save()
            return Response({'message': 'User deactivated successfully'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class AdminArticlesListView(generics.ListAPIView):
    """قائمة المقالات للأدمن"""
    permission_classes = [IsAdmin]
    serializer_class = ArticleListSerializer
    queryset = Article.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        status_filter = self.request.query_params.get('status')

        if search:
            queryset = queryset.filter(title__icontains=search)

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.select_related('author', 'category', 'assigned_reviewer', 'nominated_journal').order_by('-created_at')


class AdminArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """تفاصيل المقال وتعديله وحذفه"""
    permission_classes = [IsAdmin]
    serializer_class = ArticleListSerializer
    queryset = Article.objects.all()
    lookup_field = 'slug'


class AdminCategoriesListView(generics.ListCreateAPIView):
    """قائمة التصنيفات للأدمن"""
    permission_classes = [IsAdmin]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class AdminCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """تفاصيل التصنيف وتعديله وحذفه"""
    permission_classes = [IsAdmin]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    lookup_field = 'id'


class AdminJournalsListCreateView(generics.ListCreateAPIView):
    """List & create journals for Admin Dashboard"""
    permission_classes = [IsAdmin]
    serializer_class = AdminJournalSerializer
    queryset = Journal.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(name__icontains=search) \
                   .order_by('-impact_factor')
        return qs.order_by('-impact_factor')


class AdminJournalDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete a journal"""
    permission_classes = [IsAdmin]
    serializer_class = AdminJournalSerializer
    queryset = Journal.objects.all()


class AdminArticleJournalRecommendationsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, slug):
        article = get_object_or_404(
            Article.objects.select_related('author', 'category', 'nominated_journal'),
            slug=slug,
        )
        recommendations = ArticleWorkflowService.recommend_journals(article)[:5]
        return Response({
            'article': ArticleListSerializer(article).data,
            'recommendations': JournalRecommendationSerializer(recommendations, many=True).data,
        })


class AdminArticleAssignReviewerView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, slug):
        article = get_object_or_404(Article.objects.select_related('author', 'category'), slug=slug)
        serializer = AssignArticleReviewerSerializer(data=request.data, context={'request': request, 'article': article})
        serializer.is_valid(raise_exception=True)
        review_request = serializer.save()
        return Response({
            'message': 'Reviewer assigned successfully.',
            'review_request_id': review_request.id,
            'article': ArticleListSerializer(article).data,
        }, status=status.HTTP_201_CREATED)


class AdminArticleNominateJournalView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, slug):
        article = get_object_or_404(Article.objects.select_related('author', 'category', 'nominated_journal'), slug=slug)
        serializer = NominateArticleSerializer(data=request.data, context={'request': request, 'article': article})
        serializer.is_valid(raise_exception=True)
        updated_article = serializer.save()
        return Response({
            'message': 'Article nominated successfully.',
            'article': ArticleListSerializer(updated_article).data,
        })


class AdminArticlePublishView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, slug):
        article = get_object_or_404(Article.objects.select_related('author', 'category', 'nominated_journal'), slug=slug)
        serializer = PublishArticleSerializer(data=request.data, context={'request': request, 'article': article})
        serializer.is_valid(raise_exception=True)
        updated_article = serializer.save()
        return Response({
            'message': 'Article published successfully.',
            'article': ArticleListSerializer(updated_article).data,
        })


class SendNotificationView(APIView):
    """إرسال إشعارات للكل أو لشخص معين"""
    permission_classes = [IsAdmin]

    def post(self, request):
        recipient_id = request.data.get('recipient_id')  # None = للكل
        title = request.data.get('title')
        message = request.data.get('message')
        notification_type = request.data.get('notification_type', 'system')

        if not title or not message:
            return Response(
                {'error': 'title and message are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # إرسال للكل
        if recipient_id is None:
            recipients = User.objects.all()
            count = 0
            for recipient in recipients:
                notification = Notification.objects.create(
                    recipient=recipient,
                    sender=request.user,
                    notification_type=notification_type,
                    title=title,
                    message=message
                )
                send_notification(recipient, notification)
                count += 1

            return Response({
                'message': f'Sent notification to {count} users'
            })

        # إرسال لشخص معين
        try:
            recipient = User.objects.get(id=recipient_id)
            notification = Notification.objects.create(
                recipient=recipient,
                sender=request.user,
                notification_type=notification_type,
                title=title,
                message=message
            )
            send_notification(recipient, notification)

            return Response({
                'message': 'Notification sent successfully'
            })
        except User.DoesNotExist:
            return Response(
                {'error': 'Recipient not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class AdminArticleAcceptView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, slug):
        article = get_object_or_404(Article.objects.select_related('author', 'category'), slug=slug)
        
        # Change status
        article.status = Article.Status.NOMINATED
        article.save(update_fields=['status'])

        # Send notification
        send_notification(
            recipient=article.author,
            sender=request.user,
            notification_type='review',
            title='Your article has been accepted!',
            message=f'Your article "{article.title}" has been accepted and will be nominated to a journal.',
            article_slug=article.slug,
        )

        return Response({
            'message': 'Article accepted successfully.',
            'article': ArticleListSerializer(article).data,
        })


class AdminArticleRejectView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, slug):
        article = get_object_or_404(Article.objects.select_related('author', 'category'), slug=slug)
        rejection_reason = request.data.get('rejection_reason', '')
        
        # Change status
        article.status = Article.Status.REJECTED
        article.save(update_fields=['status'])

        # Send notification
        send_notification(
            recipient=article.author,
            sender=request.user,
            notification_type='review',
            title='Your article has been rejected.',
            message=f'Your article "{article.title}" has been rejected. {rejection_reason}',
            article_slug=article.slug,
        )

        return Response({
            'message': 'Article rejected successfully.',
            'article': ArticleListSerializer(article).data,
        })

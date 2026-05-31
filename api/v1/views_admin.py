from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Count, Q

from apps.accounts.models import User
from apps.accounts.serializers import UserSerializer
from apps.articles.models import Article, Journal
from apps.articles.serializers import ArticleListSerializer
from .admin_serializers import AdminJournalSerializer

from apps.categories.models import Category
from apps.categories.serializers import CategorySerializer
from apps.notify.models import Notification
from apps.notify.serializers import NotificationSerializer
from apps.notify.utils import send_notification
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
        
        return Response({
            'total_users': total_users,
            'total_articles': total_articles,
            'under_review': under_review,
            'published': published,
        })


class AdminUsersListView(generics.ListAPIView):
    """قائمة المستخدمين للأدمن"""
    permission_classes = [IsAdmin]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    
    def get_queryset(self):
        queryset = super().get_queryset()
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
    queryset = User.objects.all()
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
        
        return queryset.select_related('author', 'category').order_by('-created_at')


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

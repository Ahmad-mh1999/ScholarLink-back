from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from apps.reviews.models import Review, ReviewRequest
from apps.reviews.serializers import ReviewSerializer, ReviewRequestSerializer
from apps.articles.models import Article
from apps.accounts.models import User
from apps.notify.utils import notify_review
from apps.points.utils import award_points
from common.permissions import IsReviewerOrReadOnly
from common.pagination import StandardPagination


class ReviewListView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        slug = self.kwargs['slug']
        return Review.objects.filter(
            article__slug=slug
        ).select_related('reviewer')

    def perform_create(self, serializer):
        article = get_object_or_404(Article, slug=self.kwargs['slug'])
        review = serializer.save(reviewer=self.request.user, article=article)
        notify_review(article, self.request.user)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewerOrReadOnly]


# ─── لوحة تحكم المراجع ───

class ReviewerDashboardView(generics.ListAPIView):
    serializer_class = ReviewRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        status_filter = self.request.query_params.get('status', 'pending')
        return ReviewRequest.objects.filter(
            reviewer=self.request.user,
            status=status_filter
        ).select_related('article', 'assigned_by')


class AssignReviewerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug, author=request.user)
        reviewer_username = request.data.get('reviewer_username')
        message = request.data.get('message', '')

        reviewer = get_object_or_404(User, username=reviewer_username)

        if reviewer == request.user:
            return Response(
                {'error': 'لا يمكنك تعيين نفسك كمراجع'},
                status=status.HTTP_400_BAD_REQUEST
            )

        review_request, created = ReviewRequest.objects.get_or_create(
            article=article,
            reviewer=reviewer,
            defaults={
                'assigned_by': request.user,
                'message': message
            }
        )

        if not created:
            return Response(
                {'error': 'تم إرسال طلب مراجعة لهذا المراجع مسبقاً'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'message': f'تم إرسال طلب المراجعة إلى {reviewer.get_full_name()}',
            'request_id': review_request.id
        }, status=status.HTTP_201_CREATED)


class RespondToReviewRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        review_request = get_object_or_404(
            ReviewRequest,
            pk=pk,
            reviewer=request.user
        )
        action = request.data.get('action')

        if action == 'accept':
            review_request.status = 'accepted'
            review_request.save()
            return Response({'message': 'تم قبول طلب المراجعة'})

        elif action == 'reject':
            review_request.status = 'rejected'
            review_request.save()
            return Response({'message': 'تم رفض طلب المراجعة'})

        return Response(
            {'error': 'الإجراء غير صحيح. استخدم accept أو reject'},
            status=status.HTTP_400_BAD_REQUEST
        )


class SubmitReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        review_request = get_object_or_404(
            ReviewRequest,
            pk=pk,
            reviewer=request.user,
            status='accepted'
        )

        feedback = request.data.get('feedback', '')
        rating = request.data.get('rating', 0)
        decision = request.data.get('decision')
        is_anonymous = request.data.get('is_anonymous', False)

        if decision not in ['approved', 'rejected', 'revision']:
            return Response(
                {'error': 'القرار يجب أن يكون: approved أو rejected أو revision'},
                status=status.HTTP_400_BAD_REQUEST
            )

        review, created = Review.objects.get_or_create(
            article=review_request.article,
            reviewer=request.user,
            defaults={
                'review_request': review_request,
                'feedback': feedback,
                'rating': rating,
                'status': decision,
                'is_anonymous': is_anonymous
            }
        )

        if not created:
            return Response(
                {'error': 'لقد قدمت مراجعة لهذا المقال مسبقاً'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if decision == 'approved':
            review_request.article.status = 'published'
            review_request.article.save()

            # إشعار لصاحب الورقة عند الموافقة عليها
            from apps.notify.utils import send_notification
            send_notification(
                recipient=review_request.article.author,
                sender=request.user,
                notification_type='system',
                title='تمت الموافقة على ورقتك',
                message=f'تمت الموافقة على ورقتك "{review_request.article.title}" بنجاح.',
                article_slug=review_request.article.slug,
            )

        notify_review(review_request.article, request.user)

        award_points(request.user, 'submit_review')

        return Response({
            'message': 'تم تقديم المراجعة بنجاح',
            'decision': decision
        }, status=status.HTTP_201_CREATED)
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.articles.models import Article
from apps.notify.utils import send_notification
from apps.points.utils import award_points


class ArticleSubmissionModerateView(APIView):
    """endpoint يسميه frontend: POST /api/v1/articles/submission/moderate/"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # الواجهة المتوقعة من frontend غير واضحة، فسنقبل عدة أشكال شائعة:
        # - article_id
        # - slug
        # - review_request_id (اختياري)
        decision = request.data.get('decision') or request.data.get('action')
        if decision not in ['approved', 'rejected']:
            return Response({'error': 'Invalid decision. Use approved or rejected.'}, status=status.HTTP_400_BAD_REQUEST)

        article = None
        article_id = request.data.get('article_id')
        slug = request.data.get('slug')

        if article_id is not None:
            article = get_object_or_404(Article, id=article_id)
        elif slug:
            article = get_object_or_404(Article, slug=slug)
        else:
            return Response({'error': 'article_id or slug is required'}, status=status.HTTP_400_BAD_REQUEST)

        if decision == 'approved':
            article.status = Article.Status.PUBLISHED
            article.published_at = timezone.now()
            article.save()

            send_notification(
                recipient=article.author,
                sender=request.user,
                notification_type='system',
                title='تمت الموافقة على ورقتك',
                message=f'تمت الموافقة على ورقتك "{article.title}" ونشرها بنجاح.',
                article_slug=article.slug,
            )

            # points (اختياري لكن منطقي)
            try:
                award_points(request.user, 'publish_article')
            except Exception:
                pass

            return Response({'message': 'Article approved and published successfully'}, status=status.HTTP_200_OK)

        # rejected
        article.status = Article.Status.REJECTED
        article.save()
        return Response({'message': 'Article rejected successfully'}, status=status.HTTP_200_OK)


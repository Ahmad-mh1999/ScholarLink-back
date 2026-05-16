from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from apps.comments.models import Comment
from apps.comments.serializers import CommentSerializer
from apps.articles.models import Article
from apps.points.utils import award_points
from apps.notify.utils import notify_comment
from common.permissions import IsAuthorOrReadOnly
from common.pagination import SmallPagination


class CommentListView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = SmallPagination

    def get_queryset(self):
        slug = self.kwargs['slug']
        return Comment.objects.filter(
            article__slug=slug,
            parent=None,
            is_active=True
        ).select_related('author')

    def perform_create(self, serializer):
        article = get_object_or_404(Article, slug=self.kwargs['slug'])
        parent_id = self.request.data.get('parent_id')
        parent = Comment.objects.filter(id=parent_id).first() if parent_id else None
        comment = serializer.save(
            author=self.request.user,
            article=article,
            parent=parent
        )
        award_points(article.author, 'receive_comment')
        notify_comment(article, self.request.user, comment.content)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly]


class CommentLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        if request.user in comment.liked_by.all():
            comment.liked_by.remove(request.user)
            comment.likes_count -= 1
        else:
            comment.liked_by.add(request.user)
            comment.likes_count += 1
        comment.save()
        return Response({'likes_count': comment.likes_count})
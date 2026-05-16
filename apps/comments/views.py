from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.articles.models import Article
from .models import Comment
from apps.notify.utils import notify_comment



@login_required
def comment_create_view(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if request.method == 'POST':
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        parent = Comment.objects.filter(id=parent_id).first() if parent_id else None
        comment = Comment.objects.create(
            article=article,
            author=request.user,
            content=content,
            parent=parent
        )
        # إشعار لصاحب الورقة عند التعليق
        notify_comment(article, request.user, content)

    return redirect('articles:detail', slug=slug)


@login_required
def comment_delete_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    slug = comment.article.slug
    comment.delete()
    return redirect('articles:detail', slug=slug)


@login_required
def comment_like_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user in comment.liked_by.all():
        comment.liked_by.remove(request.user)
        comment.likes_count -= 1
    else:
        comment.liked_by.add(request.user)
        comment.likes_count += 1
    comment.save()
    return redirect('articles:detail', slug=comment.article.slug)
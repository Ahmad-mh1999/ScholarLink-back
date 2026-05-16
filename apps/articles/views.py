from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Article
from .forms import ArticleForm
from apps.categories.models import Category
from apps.notify.utils import send_notification


def home_view(request):
    articles = Article.objects.filter(status='published')
    categories = Category.objects.all()
    featured = articles.filter(is_featured=True)[:3]

    category_slug = request.GET.get('category')
    if category_slug:
        articles = articles.filter(category__slug=category_slug)

    paginator = Paginator(articles, 10)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    return render(request, 'articles/home.html', {
        'articles': articles,
        'categories': categories,
        'featured': featured,
    })


def article_detail_view(request, slug):
    article = get_object_or_404(Article, slug=slug, status='published')
    article.views_count += 1
    article.save()
    comments = article.comments.filter(parent=None, is_active=True)
    related = Article.objects.filter(
        category=article.category,
        status='published'
    ).exclude(id=article.id)[:3]

    return render(request, 'articles/detail.html', {
        'article': article,
        'comments': comments,
        'related': related,
    })


@login_required
def article_create_view(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m()

            # إشعار لصاحب الورقة عند إنشاء/نشر الورقة
            if article.status == Article.Status.PUBLISHED:
                send_notification(
                    recipient=article.author,
                    sender=article.author,
                    notification_type='system',
                    title='تم نشر ورقتك',
                    message=f'تم نشر ورقتك بنجاح: "{article.title}"',
                    article_slug=article.slug,
                )

            messages.success(request, 'Article created successfully!')
            return redirect('articles:detail', slug=article.slug)

    else:
        form = ArticleForm()

    return render(request, 'articles/create.html', {'form': form})


@login_required
def article_update_view(request, slug):
    article = get_object_or_404(Article, slug=slug, author=request.user)
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Article updated!')
            return redirect('articles:detail', slug=article.slug)
    else:
        form = ArticleForm(instance=article)

    return render(request, 'articles/update.html', {'form': form})


@login_required
def article_delete_view(request, slug):
    article = get_object_or_404(Article, slug=slug, author=request.user)
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Article deleted!')
        return redirect('articles:home')

    return render(request, 'articles/delete.html', {'article': article})


@login_required
def article_like_view(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if request.user in article.liked_by.all():
        article.liked_by.remove(request.user)
        article.likes_count -= 1
    else:
        article.liked_by.add(request.user)
        article.likes_count += 1

    article.save()

    from apps.notify.utils import notify_like

    notify_like(article, request.user)

    return redirect('articles:detail', slug=slug)


def explore_view(request):
    """لوحة استكشاف المقالات حسب الفئة مع تصميم جذاب."""
    # المطلوب: جلب المقالات لكل المستخدمين (أي لا تقييد بكون المستخدم Admin)
    # سنعرض كل المقالات المنشورة (status='published') مع الفئات.
    articles_qs = Article.objects.filter(status=Article.Status.PUBLISHED).select_related('category', 'author')
    categories = Category.objects.all()

    selected_category = request.GET.get('category')
    if selected_category:
        articles_qs = articles_qs.filter(category__slug=selected_category)

    search = request.GET.get('search')
    if search:
        articles_qs = articles_qs.filter(title__icontains=search)

    paginator = Paginator(articles_qs.order_by('-created_at'), 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'articles/explore.html', {
        'articles': page_obj,
        'categories': categories,
        'is_paginated': page_obj.paginator.num_pages > 1,
        'page_obj': page_obj,
        'selected_category': selected_category,
    })



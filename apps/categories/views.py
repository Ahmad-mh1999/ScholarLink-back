from django.shortcuts import render, get_object_or_404
from .models import Category
from apps.articles.models import Article


def category_list_view(request):
    categories = Category.objects.all()
    return render(request, 'categories/list.html', {'categories': categories})


def category_detail_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles = Article.objects.filter(category=category, status='published')
    return render(request, 'categories/detail.html', {
        'category': category,
        'articles': articles,
    })
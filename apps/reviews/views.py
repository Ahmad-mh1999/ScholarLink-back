from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.articles.models import Article
from .models import Review


@login_required
def review_create_view(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if request.method == 'POST':
        feedback = request.POST.get('feedback')
        rating = request.POST.get('rating', 0)
        is_anonymous = request.POST.get('is_anonymous') == 'on'
        Review.objects.create(
            article=article,
            reviewer=request.user,
            feedback=feedback,
            rating=rating,
            is_anonymous=is_anonymous
        )
        messages.success(request, 'Review submitted!')
        return redirect('articles:detail', slug=slug)
    return render(request, 'reviews/create.html', {'article': article})


@login_required
def review_update_view(request, pk):
    review = get_object_or_404(Review, pk=pk, reviewer=request.user)
    if request.method == 'POST':
        review.feedback = request.POST.get('feedback')
        review.rating = request.POST.get('rating', 0)
        review.status = request.POST.get('status')
        review.save()
        messages.success(request, 'Review updated!')
        return redirect('articles:detail', slug=review.article.slug)
    return render(request, 'reviews/update.html', {'review': review})
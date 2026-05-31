from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from apps.articles.models import Article
from apps.accounts.models import User
from .models import Review, ReviewRequest, Journal
from .serializers import ReviewSerializer, ReviewRequestSerializer, JournalSerializer


# ==================== Template Views ====================

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


# ==================== API ViewSets ====================

class JournalViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Journal model.
    Provides CRUD operations for journals.
    """
    queryset = Journal.objects.filter(is_active=True)
    serializer_class = JournalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['field_of_study', 'categories']
    search_fields = ['title', 'issn', 'publisher', 'field_of_study']
    ordering_fields = ['title', 'impact_factor', 'created_at']
    ordering = ['title']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return []

    @action(detail=False, methods=['get'])
    def recommend(self, request):
        """
        Recommend journals based on article category/field.
        Query params: category_id, field_of_study
        """
        category_id = request.query_params.get('category_id')
        field_of_study = request.query_params.get('field_of_study')
        
        queryset = self.queryset
        
        if category_id:
            queryset = queryset.filter(categories__id=category_id)
        if field_of_study:
            queryset = queryset.filter(field_of_study__icontains=field_of_study)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ReviewRequestViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for ReviewRequest model.
    Allows admins to assign reviewers to articles.
    """
    queryset = ReviewRequest.objects.all()
    serializer_class = ReviewRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'article', 'reviewer']
    search_fields = ['article__title', 'reviewer__email']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admins can see all review requests
        # Reviewers can only see their own review requests
        if user.role == User.Role.REVIEWER:
            queryset = queryset.filter(reviewer=user)
        elif user.role == User.Role.USER:
            # Regular users can see review requests for their own articles
            queryset = queryset.filter(article__author=user)
        
        return queryset

    def perform_create(self, serializer):
        # Only admins can assign reviewers
        if self.request.user.role != User.Role.ADMIN:
            raise PermissionError("Only admins can assign reviewers.")
        serializer.save(assigned_by=self.request.user)

    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """
        Get review requests for the current user (reviewer).
        """
        if request.user.role != User.Role.REVIEWER:
            return Response(
                {'error': 'Only reviewers can access their requests.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.queryset.filter(reviewer=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """
        Accept a review request.
        """
        review_request = self.get_object()
        
        if review_request.reviewer != request.user:
            return Response(
                {'error': 'You can only accept your own review requests.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if review_request.status != ReviewRequest.Status.PENDING:
            return Response(
                {'error': 'This review request is not pending.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        review_request.status = ReviewRequest.Status.ACCEPTED
        review_request.save()
        
        # Create a pending review
        Review.objects.create(
            article=review_request.article,
            reviewer=request.user,
            review_request=review_request,
            status=Review.Status.IN_PROGRESS
        )
        
        serializer = self.get_serializer(review_request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject a review request.
        """
        review_request = self.get_object()
        
        if review_request.reviewer != request.user:
            return Response(
                {'error': 'You can only reject your own review requests.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if review_request.status != ReviewRequest.Status.PENDING:
            return Response(
                {'error': 'This review request is not pending.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        review_request.status = ReviewRequest.Status.REJECTED
        review_request.save()
        
        serializer = self.get_serializer(review_request)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Review model.
    Allows reviewers to submit evaluations for articles.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'article', 'reviewer']
    search_fields = ['article__title', 'feedback']
    ordering_fields = ['created_at', 'updated_at', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admins can see all reviews
        # Reviewers can only see their own reviews
        if user.role == User.Role.REVIEWER:
            queryset = queryset.filter(reviewer=user)
        elif user.role == User.Role.USER:
            # Regular users can see reviews for their own articles
            queryset = queryset.filter(article__author=user)
        
        return queryset

    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        """
        Get reviews submitted by the current user (reviewer).
        """
        if request.user.role != User.Role.REVIEWER:
            return Response(
                {'error': 'Only reviewers can access their reviews.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.queryset.filter(reviewer=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def article_reviews(self, request):
        """
        Get all reviews for a specific article.
        Query param: article_id
        """
        article_id = request.query_params.get('article_id')
        if not article_id:
            return Response(
                {'error': 'article_id parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.queryset.filter(article_id=article_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Submit a review (change status from in_progress to approved/rejected/revision).
        """
        review = self.get_object()
        
        if review.reviewer != request.user:
            return Response(
                {'error': 'You can only submit your own reviews.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        if new_status not in [Review.Status.APPROVED, Review.Status.REJECTED, Review.Status.REVISION]:
            return Response(
                {'error': 'Invalid status. Must be approved, rejected, or revision.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        review.status = new_status
        review.feedback = request.data.get('feedback', review.feedback)
        review.rating = request.data.get('rating', review.rating)
        review.save()
        
        serializer = self.get_serializer(review)
        return Response(serializer.data)
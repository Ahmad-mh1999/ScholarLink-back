from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from apps.articles.models import Article
from .models import UserPoints, PointTransaction, JournalGuideline
from .serializers import UserPointsSerializer, PointTransactionSerializer, JournalGuidelineSerializer


class JournalGuidelineViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for JournalGuideline model.
    Provides CRUD operations for journal formatting guidelines.
    """
    queryset = JournalGuideline.objects.filter(is_active=True)
    serializer_class = JournalGuidelineSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']
    ordering = ['title']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return []


class UserPointsViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for UserPoints model.
    Provides operations for managing user points and transactions.
    """
    queryset = UserPoints.objects.all()
    serializer_class = UserPointsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.role != 'admin':
            queryset = queryset.filter(user=user)
        return queryset

    @action(detail=False, methods=['post'])
    def expedite_review(self, request):
        """
        Expedite review for an article by deducting 50 points.
        Request body: { "article_id": <article_id> }
        """
        article_id = request.data.get('article_id')
        points_cost = 50

        if not article_id:
            return Response(
                {'error': 'article_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_points = request.user.points
            if user_points.total < points_cost:
                return Response(
                    {'error': f'Insufficient points. You need {points_cost} points to expedite review.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            article = Article.objects.get(id=article_id, author=request.user)
            
            # Check if article is already priority
            if article.is_priority:
                return Response(
                    {'error': 'This article is already marked as priority.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Deduct points
            user_points.total -= points_cost
            user_points.save(update_fields=['total'])
            
            # Check cost coverage eligibility after deduction
            user_points.check_cost_coverage_eligibility()

            # Create transaction record
            PointTransaction.objects.create(
                user=request.user,
                points=-points_cost,
                reason=PointTransaction.Reason.EXPEDITE_REVIEW
            )

            # Mark article as priority
            article.is_priority = True
            article.save(update_fields=['is_priority'])

            return Response({
                'message': 'Review expedited successfully',
                'points_remaining': user_points.total,
                'article_priority': article.is_priority
            })

        except Article.DoesNotExist:
            return Response(
                {'error': 'Article not found or you are not the author'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def check_formatting_eligibility(self, request):
        """
        Check if user is eligible for auto-formatting based on points.
        Returns formatting guidelines and eligibility status.
        """
        user_points = request.user.points
        guidelines = JournalGuideline.objects.filter(is_active=True).first()
        
        # High points threshold: 500 points for auto-formatting
        is_eligible_for_auto_formatting = user_points.total >= 500
        is_eligible_for_cost_coverage = user_points.eligible_for_cost_coverage

        serializer = JournalGuidelineSerializer(guidelines) if guidelines else None

        return Response({
            'user_points': user_points.total,
            'eligible_for_auto_formatting': is_eligible_for_auto_formatting,
            'eligible_for_cost_coverage': is_eligible_for_cost_coverage,
            'guidelines': serializer.data if serializer else None
        })

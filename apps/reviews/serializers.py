from rest_framework import serializers
from .models import Review, ReviewRequest, Journal
from apps.accounts.serializers import UserSerializer
from apps.articles.serializers import ArticleListSerializer
from apps.categories.serializers import CategorySerializer


class JournalSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Journal
        fields = [
            'id', 'title', 'issn', 'field_of_study', 'categories',
            'description', 'publisher', 'impact_factor', 'website',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ReviewRequestSerializer(serializers.ModelSerializer):
    reviewer = UserSerializer(read_only=True)
    assigned_by = UserSerializer(read_only=True)
    article = ArticleListSerializer(read_only=True)
    article_id = serializers.IntegerField(write_only=True)
    reviewer_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ReviewRequest
        fields = [
            'id', 'article', 'article_id', 'reviewer', 'reviewer_id',
            'assigned_by', 'status', 'message', 'created_at'
        ]
        read_only_fields = ['status', 'created_at']

    def validate(self, data):
        article_id = data.get('article_id')
        reviewer_id = data.get('reviewer_id')
        
        # Check if reviewer already has a pending or accepted request for this article
        from apps.accounts.models import User
        from apps.articles.models import Article
        
        try:
            article = Article.objects.get(id=article_id)
            reviewer = User.objects.get(id=reviewer_id)
            
            if ReviewRequest.objects.filter(
                article=article,
                reviewer=reviewer,
                status__in=['pending', 'accepted']
            ).exists():
                raise serializers.ValidationError(
                    'This reviewer already has a pending or accepted request for this article.'
                )
            
            # Ensure reviewer has reviewer role
            if reviewer.role != User.Role.REVIEWER:
                raise serializers.ValidationError(
                    'Selected user is not a reviewer.'
                )
                
        except Article.DoesNotExist:
            raise serializers.ValidationError({'article_id': 'Article not found.'})
        except User.DoesNotExist:
            raise serializers.ValidationError({'reviewer_id': 'Reviewer not found.'})
        
        return data

    def create(self, validated_data):
        article_id = validated_data.pop('article_id')
        reviewer_id = validated_data.pop('reviewer_id')
        assigned_by = self.context['request'].user
        
        from apps.articles.models import Article
        from apps.accounts.models import User
        
        article = Article.objects.get(id=article_id)
        reviewer = User.objects.get(id=reviewer_id)
        
        review_request = ReviewRequest.objects.create(
            article=article,
            reviewer=reviewer,
            assigned_by=assigned_by,
            **validated_data
        )
        return review_request


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = UserSerializer(read_only=True)
    article = ArticleListSerializer(read_only=True)
    article_id = serializers.IntegerField(write_only=True, required=False)
    review_request_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Review
        fields = [
            'id', 'article', 'article_id', 'reviewer', 'review_request',
            'review_request_id', 'status', 'feedback', 'rating',
            'is_anonymous', 'created_at', 'updated_at'
        ]
        read_only_fields = ['reviewer', 'created_at', 'updated_at']

    def validate(self, data):
        rating = data.get('rating')
        if rating is not None and (rating < 1 or rating > 5):
            raise serializers.ValidationError({'rating': 'Rating must be between 1 and 5.'})
        return data

    def create(self, validated_data):
        article_id = validated_data.pop('article_id', None)
        review_request_id = validated_data.pop('review_request_id', None)
        reviewer = self.context['request'].user
        
        from apps.articles.models import Article
        
        if article_id:
            article = Article.objects.get(id=article_id)
        elif review_request_id:
            review_request = ReviewRequest.objects.get(id=review_request_id)
            article = review_request.article
            # Link review to review request
            validated_data['review_request'] = review_request
        else:
            raise serializers.ValidationError('Either article_id or review_request_id is required.')
        
        # Check if reviewer already reviewed this article
        if Review.objects.filter(article=article, reviewer=reviewer).exists():
            raise serializers.ValidationError('You have already reviewed this article.')
        
        review = Review.objects.create(
            article=article,
            reviewer=reviewer,
            **validated_data
        )
        return review

    def update(self, instance, validated_data):
        # Only allow reviewer to update their own review
        if instance.reviewer != self.context['request'].user:
            raise serializers.ValidationError('You can only update your own reviews.')
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
from rest_framework import serializers

from apps.accounts.models import User
from apps.articles.models import Article, Journal
from apps.articles.serializers import ArticleListSerializer, JournalSerializer
from apps.articles.services import ArticleWorkflowService


class AdminJournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = [
            'id',
            'name',
            'field_of_study',
            'impact_factor',
            'publication_type',
            'publication_fee',
            'font_guidelines',
            'margin_guidelines',
            'figure_guidelines',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AssignArticleReviewerSerializer(serializers.Serializer):
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.REVIEWER),
        source='reviewer'
    )
    message = serializers.CharField(required=False, allow_blank=True)

    def save(self, **kwargs):
        article = self.context['article']
        assigned_by = self.context['request'].user
        reviewer = self.validated_data['reviewer']
        message = self.validated_data.get('message', '')
        return ArticleWorkflowService.assign_reviewer(article, reviewer, assigned_by, message)


class NominateArticleSerializer(serializers.Serializer):
    journal_id = serializers.PrimaryKeyRelatedField(
        queryset=Journal.objects.all(),
        source='journal'
    )

    def save(self, **kwargs):
        article = self.context['article']
        journal = self.validated_data['journal']
        return ArticleWorkflowService.nominate_journal(article, journal)


class PublishArticleSerializer(serializers.Serializer):
    def save(self, **kwargs):
        article = self.context['article']
        return ArticleWorkflowService.publish_article(article)


class JournalRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = ['id', 'name', 'field_of_study', 'impact_factor', 'publication_type', 'publication_fee']

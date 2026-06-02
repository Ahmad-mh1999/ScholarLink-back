from django.db.models import Q
from rest_framework import serializers

from apps.articles.models import Article, Journal
from apps.reviews.models import ReviewRequest


class ArticleWorkflowService:
    @staticmethod
    def get_article_field(article):
        candidates = [
            getattr(getattr(article, 'category', None), 'name', ''),
            getattr(getattr(article, 'author', None), 'field_of_study', ''),
            getattr(article, 'location', ''),
        ]
        return next((value.strip() for value in candidates if value and value.strip()), '')

    @staticmethod
    def recommend_journals(article):
        """Returns top 3 Journal objects matching article field"""
        field = (article.category.name if article.category else '') or (getattr(article.author, 'field_of_study', '') if hasattr(article, 'author') else '')
        journals = Journal.objects.filter(
            is_active=True,
            field_of_study__icontains=field
        ).order_by('-impact_factor')[:3]
        if not journals:
            journals = Journal.objects.filter(is_active=True).order_by('-impact_factor')[:3]
        return journals

    @staticmethod
    def validate_formatting(article, journal):
        mismatches = {}

        if journal.font_guidelines and article.submission_font:
            if article.submission_font.strip().lower() != journal.font_guidelines.strip().lower():
                mismatches['submission_font'] = (
                    f"Expected '{journal.font_guidelines}' but got '{article.submission_font}'."
                )

        if journal.margin_guidelines and article.submission_margins:
            if article.submission_margins.strip().lower() != journal.margin_guidelines.strip().lower():
                mismatches['submission_margins'] = (
                    f"Expected '{journal.margin_guidelines}' but got '{article.submission_margins}'."
                )

        if journal.figure_guidelines and article.submission_figures:
            if article.submission_figures.strip().lower() != journal.figure_guidelines.strip().lower():
                mismatches['submission_figures'] = (
                    f"Expected '{journal.figure_guidelines}' but got '{article.submission_figures}'."
                )

        if mismatches:
            raise serializers.ValidationError({'formatting': mismatches})

    @staticmethod
    def refresh_subsidy_status(article):
        points_total = getattr(getattr(article.author, 'points', None), 'total', 0) or 0
        article.subsidy_status = (
            Article.SubsidyStatus.SUBSIDY_PENDING
            if points_total >= 1000
            else Article.SubsidyStatus.NOT_ELIGIBLE
        )
        return article.subsidy_status

    @staticmethod
    def assign_reviewer(article, reviewer, assigned_by, message=''):
        if article.assigned_reviewer_id == reviewer.id:
            raise serializers.ValidationError({'reviewer_id': 'This reviewer is already assigned to the article.'})

        if ReviewRequest.objects.filter(article=article, reviewer=reviewer).exclude(status=ReviewRequest.Status.REJECTED).exists():
            raise serializers.ValidationError({'reviewer_id': 'A pending or accepted assignment already exists for this reviewer.'})

        review_request = ReviewRequest.objects.create(
            article=article,
            reviewer=reviewer,
            assigned_by=assigned_by,
            message=message,
        )

        article.assigned_reviewer = reviewer
        if article.status == Article.Status.DRAFT:
            article.status = Article.Status.UNDER_REVIEW
        article.save(update_fields=['assigned_reviewer', 'status', 'updated_at'])
        return review_request

    @staticmethod
    def nominate_journal(article, journal):
        if article.status not in [Article.Status.UNDER_REVIEW, Article.Status.NOMINATED]:
            raise serializers.ValidationError({
                'status': 'Only articles under review can be nominated to a journal.'
            })

        ArticleWorkflowService.validate_formatting(article, journal)
        ArticleWorkflowService.refresh_subsidy_status(article)
        article.nominated_journal = journal
        article.status = Article.Status.NOMINATED
        article.save(update_fields=['nominated_journal', 'status', 'subsidy_status', 'updated_at'])
        return article

    @staticmethod
    def publish_article(article):
        if article.status != Article.Status.NOMINATED:
            raise serializers.ValidationError({
                'status': 'Only nominated articles can be published.'
            })

        article.status = Article.Status.PUBLISHED
        article.save(update_fields=['status', 'published_at', 'updated_at'])
        return article

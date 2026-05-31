from rest_framework import serializers
from .models import UserPoints, PointTransaction, JournalGuideline
from apps.accounts.serializers import UserSerializer


class JournalGuidelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalGuideline
        fields = [
            'id', 'title', 'font_size', 'margins', 'line_spacing',
            'image_dimensions', 'citation_style', 'max_word_count',
            'min_word_count', 'additional_requirements', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PointTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointTransaction
        fields = ['id', 'points', 'reason', 'created_at']


class UserPointsSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    transactions = PointTransactionSerializer(
        source='user.transactions',
        many=True,
        read_only=True
    )

    class Meta:
        model = UserPoints
        fields = ['user', 'total', 'eligible_for_cost_coverage', 'transactions', 'updated_at']
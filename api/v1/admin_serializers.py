from rest_framework import serializers

from apps.articles.models import Journal


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


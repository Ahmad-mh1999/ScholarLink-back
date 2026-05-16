from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    articles_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'description', 'articles_count']

    def get_articles_count(self, obj):
        return obj.articles.filter(status='published').count()
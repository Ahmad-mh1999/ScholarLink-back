from rest_framework import serializers
from .models import Article, ArticleRating, Bookmark
from apps.accounts.serializers import UserSerializer
from apps.categories.serializers import CategorySerializer
from apps.categories.models import Category


class ArticleListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False
    )
    comments_count = serializers.SerializerMethodField()
    average_rating = serializers.ReadOnlyField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'description', 'abstract',
            'cover_image', 'author', 'category', 'category_id',
            'status', 'access_level', 'read_time', 'views_count',
            'likes_count', 'comments_count', 'average_rating',
            'is_featured', 'published_at', 'created_at'
        ]
        read_only_fields = ['slug', 'views_count', 'likes_count', 'published_at']

    def get_comments_count(self, obj):
        return obj.comments.count()


class ArticleDetailSerializer(ArticleListSerializer):
    class Meta(ArticleListSerializer.Meta):
        fields = ArticleListSerializer.Meta.fields + [
            'content', 'pdf_file', 'location'
        ]


class ArticleRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleRating
        fields = ['id', 'rating', 'created_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("التقييم يجب أن يكون بين 1 و 5")
        return value


class BookmarkSerializer(serializers.ModelSerializer):
    article = ArticleListSerializer(read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'article', 'created_at']


class CitationSerializer(serializers.ModelSerializer):
    citation_apa = serializers.ReadOnlyField()
    citation_mla = serializers.ReadOnlyField()
    citation_chicago = serializers.ReadOnlyField()

    class Meta:
        model = Article
        fields = ['id', 'title', 'citation_apa', 'citation_mla', 'citation_chicago']
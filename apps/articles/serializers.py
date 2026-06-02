from rest_framework import serializers
from .models import Article, ArticleRating, Bookmark, Journal
from apps.accounts.serializers import UserSerializer
from apps.categories.serializers import CategorySerializer
from apps.categories.models import Category



class JournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = [
            'id', 'name', 'issn', 'field_of_study', 'publisher', 'website',
            'impact_factor', 'publication_type', 'publication_fee', 'is_active',
            'font_guidelines', 'margin_guidelines', 'figure_guidelines',
            'citation_style', 'max_word_count', 'min_word_count', 'max_pages',
            'additional_requirements', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PublicJournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = [
            'id', 'name', 'field_of_study', 'impact_factor',
            'publication_type', 'publication_fee', 'font_guidelines',
            'margin_guidelines', 'figure_guidelines', 'citation_style',
            'max_word_count', 'min_word_count', 'max_pages',
            'additional_requirements', 'description'
        ]


class ArticleCreateSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,
        error_messages={
            'does_not_exist': 'The selected category does not exist.',
            'incorrect_type': 'Please enter a valid value for the category.'
        }
    )
    tags = serializers.CharField(required=False, allow_blank=True)
    pdf_file = serializers.FileField(
        required=True,
        error_messages={
            'required': 'Please upload the research paper (PDF).',
            'invalid': 'The uploaded file is invalid. Please upload a valid PDF file.'
        }
    )
    title = serializers.CharField(
        max_length=500,
        error_messages={
            'required': 'Research paper title is required.',
            'max_length': 'Research paper title cannot exceed 500 characters.'
        }
    )
    abstract = serializers.CharField(
        error_messages={
            'required': 'Abstract is required.'
        }
    )

    class Meta:
        model = Article
        fields = [
            'title', 'abstract', 'category_id', 'tags', 'pdf_file',
            'submission_font', 'submission_margins', 'submission_figures', 'location'
        ]

    def validate_pdf_file(self, value):
        if value:
            import os
            ext = os.path.splitext(value.name)[1].lower()
            if ext != '.pdf':
                raise serializers.ValidationError('Please upload a PDF file only.')
            if value.size > 50 * 1024 * 1024:  # 50MB max
                raise serializers.ValidationError('File size is too large. Maximum is 50MB.')
        return value

    def create(self, validated_data):
        tags_str = validated_data.pop('tags', '')
        article = Article.objects.create(**validated_data)
        if tags_str:
            tag_names = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
            article.tags.add(*tag_names)
        return article


class ArticleListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    nominated_journal = JournalSerializer(read_only=True)
    assigned_reviewer = UserSerializer(read_only=True)
    nominated_journal_id = serializers.PrimaryKeyRelatedField(
        queryset=Journal.objects.all(),
        source='nominated_journal',
        write_only=True,
        required=False,
        allow_null=True
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False
    )
    comments_count = serializers.SerializerMethodField()
    average_rating = serializers.ReadOnlyField()
    author_name = serializers.SerializerMethodField()
    author_role = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    image = serializers.ImageField(source='cover_image', read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'description', 'abstract',
            'cover_image', 'image', 'author', 'category', 'category_id',
            'status', 'read_time', 'views_count',
            'likes_count', 'comments_count', 'average_rating',
            'is_featured', 'is_priority', 'published_at', 'created_at',
            'assigned_reviewer',
            'nominated_journal', 'nominated_journal_id', 'external_journal_accepted', 'external_journal_name',
            'submission_font', 'submission_margins', 'submission_figures',
            'subsidy_status',
            'author_name', 'author_role', 'category_name'
        ]
        read_only_fields = ['slug', 'views_count', 'likes_count', 'published_at']

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_author_name(self, obj):
        return obj.author.get_full_name() if obj.author else ''

    def get_author_role(self, obj):
        return obj.author.role if obj.author and obj.author.role else ''

    def get_category_name(self, obj):
        return obj.category.name if obj.category else ''


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

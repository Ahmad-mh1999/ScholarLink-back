from django.db import models
from django.utils.text import slugify
from taggit.managers import TaggableManager
from apps.accounts.models import User
from apps.categories.models import Category


class Article(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        UNDER_REVIEW = 'under_review', 'Under Review'
        REJECTED = 'rejected', 'Rejected'

    class AccessLevel(models.TextChoices):
        PUBLIC = 'public', 'Public'
        PRIVATE = 'private', 'Private'
        INSTITUTIONAL = 'institutional', 'Institutional'

    # ─── معلومات أساسية ───
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, unique=True, blank=True)

    # ─── المحتوى ───
    abstract = models.TextField(blank=True)       # الملخص الأكاديمي
    description = models.TextField(blank=True)    # وصف مختصر
    content = models.TextField(blank=True)        # المحتوى الكامل

    # ─── الملفات ───
    cover_image = models.ImageField(upload_to='articles/covers/', null=True, blank=True)
    pdf_file = models.FileField(upload_to='articles/pdfs/', null=True, blank=True)

    # ─── التصنيف ───
    tags = TaggableManager(blank=True)
    location = models.CharField(max_length=255, blank=True)

    # ─── الحالة ───
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    access_level = models.CharField(max_length=20, choices=AccessLevel.choices, default=AccessLevel.PUBLIC)
    is_featured = models.BooleanField(default=False)

    # ─── الإحصائيات ───
    read_time = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    citations_count = models.PositiveIntegerField(default=0)

    # ─── التفاعلات ───
    liked_by = models.ManyToManyField(User, related_name='liked_articles', blank=True)

    # ─── التواريخ ───
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    # ─── الاستشهاد ───
    @property
    def citation_apa(self):
        year = self.published_at.year if self.published_at else self.created_at.year
        return f"{self.author.get_full_name()} ({year}). {self.title}. ScholarLink Platform."

    @property
    def citation_mla(self):
        year = self.published_at.year if self.published_at else self.created_at.year
        return f'{self.author.get_full_name()}. "{self.title}." ScholarLink, {year}.'

    @property
    def citation_chicago(self):
        year = self.published_at.year if self.published_at else self.created_at.year
        return f'{self.author.get_full_name()}. {year}. "{self.title}." ScholarLink Platform.'

    # ─── متوسط التقييم ───
    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.rating for r in ratings) / ratings.count(), 1)
        return 0.0


class ArticleRating(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveIntegerField()  # 1-5

    class Meta:
        unique_together = ['article', 'user']
        ordering = ['-id']

    def __str__(self):
        return f"{self.user} rated {self.article} — {self.rating}/5"


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'article']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} bookmarked {self.article}"
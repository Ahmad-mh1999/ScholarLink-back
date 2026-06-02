from decimal import Decimal

from django.db import models
from django.utils.text import slugify
from taggit.managers import TaggableManager
from apps.accounts.models import User
from apps.categories.models import Category



class Journal(models.Model):

    class PublicationType(models.TextChoices):
        OPEN_ACCESS = 'open_access', 'Open Access'
        SUBSCRIPTION = 'subscription', 'Subscription'

    name = models.CharField(max_length=255, unique=True)
    issn = models.CharField(max_length=50, blank=True)
    field_of_study = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    impact_factor = models.DecimalField(max_digits=5, decimal_places=2)
    publication_type = models.CharField(
        max_length=20,
        choices=PublicationType.choices,
        default=PublicationType.OPEN_ACCESS
    )
    publication_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    font_guidelines = models.TextField(blank=True)
    margin_guidelines = models.TextField(blank=True)
    figure_guidelines = models.TextField(blank=True)
    citation_style = models.CharField(max_length=100, blank=True)
    max_word_count = models.PositiveIntegerField(null=True, blank=True)
    min_word_count = models.PositiveIntegerField(null=True, blank=True)
    max_pages = models.PositiveIntegerField(null=True, blank=True)
    additional_requirements = models.TextField(blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-impact_factor']
        verbose_name = 'Journal'
        verbose_name_plural = 'Journals'

    def __str__(self):
        return f"{self.name} (IF: {self.impact_factor})"


class Article(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        UNDER_REVIEW = 'under_review', 'Under Review'
        NOMINATED = 'nominated', 'Nominated'
        PUBLISHED = 'published', 'Published'
        REJECTED = 'rejected', 'Rejected'

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
    is_featured = models.BooleanField(default=False)
    is_priority = models.BooleanField(default=False, help_text="Flag for expedited review requests")
    assigned_reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_articles',
        limit_choices_to={'role': User.Role.REVIEWER},
        help_text='Reviewer currently assigned to evaluate this article'
    )

    # ─── Journal Nomination (Reviewer Evaluation) ───
    nominated_journal = models.ForeignKey(
        Journal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='nominated_articles',
        help_text="Journal nominated by reviewer or admin"
    )
    external_journal_accepted = models.BooleanField(
        default=False,
        help_text="Whether article has been accepted by external journal"
    )
    external_journal_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name of external journal that accepted the article"
    )

    # ─── Submission Formatting ───
    submission_font = models.CharField(max_length=100, blank=True)
    submission_margins = models.CharField(max_length=100, blank=True)
    submission_figures = models.TextField(blank=True)

    # ─── Subsidy Status ───
    class SubsidyStatus(models.TextChoices):
        NOT_ELIGIBLE = 'not_eligible', 'Not Eligible'
        SUBSIDY_PENDING = 'subsidy_pending', 'Subsidy Pending'
        APPROVED_FOR_COST_COVERAGE = 'approved_for_cost_coverage', 'Approved for Cost Coverage'

    subsidy_status = models.CharField(
        max_length=30,
        choices=SubsidyStatus.choices,
        default=SubsidyStatus.NOT_ELIGIBLE,
        help_text="Subsidy eligibility status based on user points"
    )

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
            base_slug = slugify(self.title)
            self.slug = base_slug
            counter = 1
            while Article.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1

        if self.assigned_reviewer and self.status == self.Status.DRAFT:
            self.status = self.Status.UNDER_REVIEW

        author_points_total = 0
        if hasattr(self.author, 'points') and self.author.points is not None:
            author_points_total = getattr(self.author.points, 'total', 0) or 0

        if author_points_total >= 1000:
            self.subsidy_status = self.SubsidyStatus.SUBSIDY_PENDING
        elif self.subsidy_status == self.SubsidyStatus.SUBSIDY_PENDING:
            self.subsidy_status = self.SubsidyStatus.NOT_ELIGIBLE

        if self.nominated_journal and self.status == self.Status.UNDER_REVIEW:
            self.status = self.Status.NOMINATED

        if self.status == self.Status.PUBLISHED and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()

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

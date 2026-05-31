from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class AcademicStatus(models.TextChoices):
        UNDERGRADUATE = 'undergraduate', 'Undergraduate'
        GRADUATE = 'graduate', 'Graduate'
        PHD = 'phd', 'PhD'
        PROFESSOR = 'professor', 'Professor'
        RESEARCHER = 'researcher', 'Researcher'
        OTHER = 'other', 'Other'

    email = models.EmailField(unique=True)
    institutional_email = models.EmailField(unique=True, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    institution = models.CharField(max_length=255, blank=True)
    field_of_study = models.CharField(max_length=255, blank=True)
    academic_status = models.CharField(
        max_length=20,
        choices=AcademicStatus.choices,
        default=AcademicStatus.UNDERGRADUATE
    )
# مثال: "السنة الثالثة" أو "دكتوراه السنة الثانية"
    location = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    orcid_id = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)

    followers = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='following',
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Role(models.TextChoices):
        USER = 'user', 'مستخدم عادي'
        REVIEWER = 'reviewer', 'مراجع أكاديمي'
        ADMIN = 'admin', 'مسؤول'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER
    )
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name()} - {self.email}"

    @property
    def posts_count(self):
        return self.articles.filter(status='published').count()

    @property
    def network_count(self):
        return self.followers.count()


class Expertise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expertise')
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    icon = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.user} - {self.title}"
    

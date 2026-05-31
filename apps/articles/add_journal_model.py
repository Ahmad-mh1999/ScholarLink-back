#!/usr/bin/env python
"""Add Journal model and update Article model with journal relationships"""

with open('models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add Journal model before Article model
journal_model = '''
class Journal(models.Model):
    
    class PublicationType(models.TextChoices):
        OPEN_ACCESS = 'open_access', 'Open Access'
        SUBSCRIPTION = 'subscription', 'Subscription'
    
    name = models.CharField(max_length=255, unique=True)
    field_of_study = models.CharField(max_length=255)
    impact_factor = models.DecimalField(max_digits=5, decimal_places=2)
    publication_type = models.CharField(
        max_length=20,
        choices=PublicationType.choices,
        default=PublicationType.OPEN_ACCESS
    )
    publication_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    font_guidelines = models.TextField(blank=True)
    margin_guidelines = models.TextField(blank=True)
    figure_guidelines = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-impact_factor']
        verbose_name = 'Journal'
        verbose_name_plural = 'Journals'
    
    def __str__(self):
        return f"{self.name} (IF: {self.impact_factor})"


'''

# Insert Journal model before Article class
if 'class Article(models.Model):' in content:
    content = content.replace('class Article(models.Model):', journal_model + 'class Article(models.Model):')
    print("Added Journal model")
else:
    print("Could not find Article class")

# Update Article model to replace journal_nomination CharField with ForeignKey
old_journal_fields = '''    # ─── Journal Nomination (Reviewer Evaluation) ───
    journal_nomination = models.CharField(
        max_length=50,
        choices=[
            ('none', 'Not Nominated'),
            ('nature', 'Nature'),
            ('science', 'Science'),
            ('cell', 'Cell'),
            ('lancet', 'The Lancet'),
            ('nejm', 'New England Journal of Medicine'),
            ('ieee', 'IEEE Transactions'),
            ('acm', 'ACM Publications'),
            ('springer', 'Springer Nature'),
            ('elsevier', 'Elsevier'),
            ('wiley', 'Wiley'),
            ('taylor', 'Taylor & Francis'),
            ('sage', 'SAGE Publications'),
            ('oxford', 'Oxford University Press'),
            ('cambridge', 'Cambridge University Press'),
            ('other', 'Other Journal')
        ],
        default='none',
        blank=True,
        help_text="Journal recommended by reviewer after evaluation"
    )
    external_journal_accepted = models.BooleanField(
        default=False,
        help_text="Whether article has been accepted by external journal"
    )
    external_journal_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name of external journal that accepted the article"
    )'''

new_journal_fields = '''    # ─── Journal Nomination (Reviewer Evaluation) ───
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
    
    # ─── Subsidy Status ───
    class SubsidyStatus(models.TextChoices):
        NOT_ELIGIBLE = 'not_eligible', 'Not Eligible'
        PENDING_REVIEW = 'pending_review', 'Pending Review'
        APPROVED_FOR_COST_COVERAGE = 'approved_for_cost_coverage', 'Approved for Cost Coverage'
    
    subsidy_status = models.CharField(
        max_length=30,
        choices=SubsidyStatus.choices,
        default=SubsidyStatus.NOT_ELIGIBLE,
        help_text="Subsidy eligibility status based on user points"
    )'''

if old_journal_fields in content:
    content = content.replace(old_journal_fields, new_journal_fields)
    print("Updated Article model with journal FK and subsidy status")
else:
    print("Could not find old journal fields to replace")

# Update the save method to include subsidy logic
old_save = '''    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)'''

new_save = '''    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Automated Financial Subsidy Trigger
        # If nominated_journal is assigned, it's open access, and author has >= 1000 points
        if self.nominated_journal and self.nominated_journal.publication_type == 'open_access':
            from apps.accounts.models import User
            try:
                author_points = self.author.points if hasattr(self.author, 'points') else 0
                if author_points >= 1000:
                    self.subsidy_status = self.SubsidyStatus.PENDING_REVIEW
            except Exception:
                pass
        
        super().save(*args, **kwargs)'''

if old_save in content:
    content = content.replace(old_save, new_save)
    print("Updated save method with subsidy logic")
else:
    print("Could not find save method to update")

with open('models.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully updated models.py")

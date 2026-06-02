from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0004_journal_article_external_journal_accepted_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='assigned_reviewer',
            field=models.ForeignKey(
                blank=True,
                help_text='Reviewer currently assigned to evaluate this article',
                limit_choices_to={'role': 'reviewer'},
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name='assigned_articles',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='article',
            name='submission_figures',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='article',
            name='submission_font',
            field=models.CharField(blank=True, default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='article',
            name='submission_margins',
            field=models.CharField(blank=True, default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='article',
            name='status',
            field=models.CharField(
                choices=[
                    ('draft', 'Draft'),
                    ('under_review', 'Under Review'),
                    ('nominated', 'Nominated'),
                    ('published', 'Published'),
                    ('rejected', 'Rejected'),
                ],
                default='draft',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='article',
            name='subsidy_status',
            field=models.CharField(
                choices=[
                    ('not_eligible', 'Not Eligible'),
                    ('subsidy_pending', 'Subsidy Pending'),
                    ('approved_for_cost_coverage', 'Approved for Cost Coverage'),
                ],
                default='not_eligible',
                help_text='Subsidy eligibility status based on user points',
                max_length=30,
            ),
        ),
    ]

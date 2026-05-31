#!/usr/bin/env python
"""Add journal nomination and external journal fields to Article model"""

with open('models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the is_priority line and add new fields after it
old_section = '''    is_priority = models.BooleanField(default=False, help_text="Flag for expedited review requests")

    # ─── الإحصائيات ───'''

new_section = '''    is_priority = models.BooleanField(default=False, help_text="Flag for expedited review requests")

    # ─── Journal Nomination (Reviewer Evaluation) ───
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
    )

    # ─── الإحصائيات ───'''

if old_section in content:
    content = content.replace(old_section, new_section)
    with open('models.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully added journal nomination fields to models.py")
else:
    print("Could not find the target section in models.py")

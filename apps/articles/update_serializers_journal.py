#!/usr/bin/env python
"""Update serializers to include Journal model and new Article fields"""

with open('serializers.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add JournalSerializer at the beginning after imports
journal_serializer = '''
class JournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = [
            'id', 'name', 'field_of_study', 'impact_factor',
            'publication_type', 'publication_fee', 'font_guidelines',
            'margin_guidelines', 'figure_guidelines', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


'''

# Insert JournalSerializer before ArticleListSerializer
if 'class ArticleListSerializer(serializers.ModelSerializer):' in content:
    content = content.replace('class ArticleListSerializer(serializers.ModelSerializer):', journal_serializer + 'class ArticleListSerializer(serializers.ModelSerializer):')
    print("Added JournalSerializer")
else:
    print("Could not find ArticleListSerializer")

# Update ArticleListSerializer to include new fields
old_fields = '''        fields = [
            'id', 'title', 'slug', 'description', 'abstract',
            'cover_image', 'author', 'category', 'category_id',
            'status', 'read_time', 'views_count',
            'likes_count', 'comments_count', 'average_rating',
            'is_featured', 'is_priority', 'published_at', 'created_at',
            'journal_nomination', 'external_journal_accepted', 'external_journal_name'
        ]'''

new_fields = '''        fields = [
            'id', 'title', 'slug', 'description', 'abstract',
            'cover_image', 'author', 'category', 'category_id',
            'status', 'read_time', 'views_count',
            'likes_count', 'comments_count', 'average_rating',
            'is_featured', 'is_priority', 'published_at', 'created_at',
            'nominated_journal', 'external_journal_accepted', 'external_journal_name',
            'subsidy_status'
        ]'''

if old_fields in content:
    content = content.replace(old_fields, new_fields)
    print("Updated ArticleListSerializer fields")
else:
    print("Could not find ArticleListSerializer fields to update")

# Add nested serializer for nominated_journal
old_author_line = '''    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)'''

new_author_line = '''    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    nominated_journal = JournalSerializer(read_only=True)'''

if old_author_line in content:
    content = content.replace(old_author_line, new_author_line)
    print("Added nominated_journal nested serializer")
else:
    print("Could not add nominated_journal nested serializer")

with open('serializers.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully updated serializers.py")

#!/usr/bin/env python
"""Update serializers to include journal nomination fields"""

with open('serializers.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Update ArticleListSerializer fields
old_fields = '''        fields = [
            'id', 'title', 'slug', 'description', 'abstract',
            'cover_image', 'author', 'category', 'category_id',
            'status', 'read_time', 'views_count',
            'likes_count', 'comments_count', 'average_rating',
            'is_featured', 'published_at', 'created_at'
        ]'''

new_fields = '''        fields = [
            'id', 'title', 'slug', 'description', 'abstract',
            'cover_image', 'author', 'category', 'category_id',
            'status', 'read_time', 'views_count',
            'likes_count', 'comments_count', 'average_rating',
            'is_featured', 'is_priority', 'published_at', 'created_at',
            'journal_nomination', 'external_journal_accepted', 'external_journal_name'
        ]'''

if old_fields in content:
    content = content.replace(old_fields, new_fields)
    with open('serializers.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully updated serializers.py")
else:
    print("Could not find the target section in serializers.py")

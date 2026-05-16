from django_filters import FilterSet, DateFilter, BooleanFilter, CharFilter
from django.utils import timezone
from datetime import timedelta
from .models import Article
from django_filters import FilterSet, DateFilter, CharFilter, BooleanFilter
from django.utils import timezone
from datetime import timedelta
from .models import Article


class ArticleFilter(FilterSet):
    date_from = DateFilter(field_name='published_at', lookup_expr='gte')
    date_to = DateFilter(field_name='published_at', lookup_expr='lte')
    author = CharFilter(field_name='author__username', lookup_expr='iexact')
    tag = CharFilter(field_name='tags__name', lookup_expr='iexact')
    this_week = BooleanFilter(method='filter_this_week')
    this_month = BooleanFilter(method='filter_this_month')
    this_year = BooleanFilter(method='filter_this_year')

    class Meta:
        model = Article
        fields = [
            'category__slug', 'status', 'access_level',
            'is_featured', 'date_from', 'date_to',
            'author', 'tag', 'this_week', 'this_month', 'this_year'
        ]

    def filter_this_week(self, queryset, name, value):
        if value:
            return queryset.filter(
                published_at__gte=timezone.now() - timedelta(days=7)
            )
        return queryset

    def filter_this_month(self, queryset, name, value):
        if value:
            now = timezone.now()
            return queryset.filter(
                published_at__year=now.year,
                published_at__month=now.month
            )
        return queryset

    def filter_this_year(self, queryset, name, value):
        if value:
            return queryset.filter(
                published_at__year=timezone.now().year
            )
        return queryset
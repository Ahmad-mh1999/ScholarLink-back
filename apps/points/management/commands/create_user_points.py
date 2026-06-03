
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.points.models import UserPoints


class Command(BaseCommand):
    help = 'Creates UserPoints objects for existing users who don\'t have them'

    def handle(self, *args, **options):
        users_without_points = User.objects.filter(points__isnull=True)
        count = 0
        for user in users_without_points:
            UserPoints.objects.create(user=user)
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} UserPoints objects'))

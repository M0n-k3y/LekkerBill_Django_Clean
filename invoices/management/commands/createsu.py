import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    """
    Creates a superuser from environment variables if one does not exist.
    This is safe to run on every deployment.
    """
    help = 'Creates a superuser from environment variables if one does not exist'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not all([username, email, password]):
            self.stdout.write(self.style.WARNING(
                'Superuser environment variables (DJANGO_SUPERUSER_USERNAME, etc.) not set. Skipping creation.'
            ))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" already exists. No action taken.'))
        else:
            self.stdout.write(self.style.NOTICE(f'Creating superuser "{username}"...'))
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created successfully.'))
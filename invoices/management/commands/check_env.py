# F:/Python Apps/LekkerBill_Django_Clean/invoices/management/commands/check_env.py

import os
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    Checks and prints the status of critical environment variables for debugging on Railway.
    """
    help = 'Checks and prints the status of critical environment variables.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("--- Checking Environment Variables ---"))

        required_vars = [
            'SECRET_KEY',
            'DEBUG',
            'DATABASE_URL',
            'DJANGO_SUPERUSER_USERNAME',
            'DJANGO_SUPERUSER_EMAIL',
            'DJANGO_SUPERUSER_PASSWORD',
            'PAYFAST_MERCHANT_ID',
            'PAYFAST_MERCHANT_KEY',
            'PAYFAST_PASSPHRASE',
            'PAYFAST_TESTING',
        ]

        all_found = True
        for var in required_vars:
            value = os.getenv(var)
            if value:
                # Don't print sensitive values, just confirm they exist
                if var in ['SECRET_KEY', 'DATABASE_URL', 'DJANGO_SUPERUSER_PASSWORD', 'PAYFAST_MERCHANT_KEY', 'PAYFAST_PASSPHRASE']:
                    self.stdout.write(self.style.SUCCESS(f"✅ {var}: Found"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"✅ {var}: Found (Value: {value})"))
            else:
                self.stdout.write(self.style.ERROR(f"❌ {var}: NOT FOUND"))
                all_found = False

        if not all_found:
            self.stdout.write(self.style.ERROR("\nFATAL: One or more required environment variables are missing. Deployment will fail."))
        else:
            self.stdout.write(self.style.SUCCESS("\nSUCCESS: All checked environment variables are present."))

        self.stdout.write(self.style.NOTICE("--- Finished Checking Environment Variables ---"))
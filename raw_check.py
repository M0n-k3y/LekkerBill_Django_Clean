# F:/Python Apps/LekkerBill_Django_Clean/raw_check.py
import os
import sys

print("--- RAW ENVIRONMENT CHECK INITIATED ---")
print("This script does not use Django and runs first to debug the environment.")

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
    'RAILWAY_PUBLIC_DOMAIN'
]

all_found = True
for var in required_vars:
    value = os.getenv(var)
    if value:
        # Don't print sensitive values, just confirm they exist
        if var in ['SECRET_KEY', 'DATABASE_URL', 'DJANGO_SUPERUSER_PASSWORD', 'PAYFAST_MERCHANT_KEY', 'PAYFAST_PASSPHRASE']:
            print(f"✅ {var}: Found")
        else:
            print(f"✅ {var}: Found (Value: {value})")
    else:
        print(f"❌ {var}: NOT FOUND")
        all_found = False

print("--- RAW ENVIRONMENT CHECK COMPLETE ---")

if not all_found:
    print("\nFATAL: One or more required environment variables are missing. Deployment will fail.")
    # Exit with a non-zero status code to halt the release phase
    sys.exit(1)
else:
    print("\nSUCCESS: All checked environment variables are present. Proceeding with deployment...")
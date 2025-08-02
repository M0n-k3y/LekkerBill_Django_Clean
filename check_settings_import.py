# F:/Python Apps/LekkerBill_Django_Clean/check_settings_import.py
import os
import sys

print("--- DJANGO FULL SETUP CHECK INITIATED ---")
print("This script will attempt to fully initialize the Django application.")

try:
    # Set the DJANGO_SETTINGS_MODULE environment variable just like manage.py does
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lekkerbill.settings')

    # Import the core django library
    import django

    # This is the critical function that loads the settings, configures logging,
    # and populates the application registry. This is the step that is failing.
    print("Attempting to run django.setup()...")
    django.setup()
    print("✅ SUCCESS: django.setup() completed without errors.")

except Exception as e:
    print(f"❌ FATAL: An exception occurred during django.setup().")
    print("--- TRACEBACK ---")
    import traceback
    # This will print the full traceback to standard output, which will appear in the deploy logs.
    traceback.print_exc()
    print("--- END TRACEBACK ---")
    # Exit with a non-zero status code to halt the release phase
    sys.exit(1)

print("--- DJANGO FULL SETUP CHECK COMPLETE ---")
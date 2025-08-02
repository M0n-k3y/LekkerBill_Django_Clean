# F:/Python Apps/LekkerBill_Django_Clean/check_settings_import.py
import os
import sys

print("--- SETTINGS IMPORT CHECK INITIATED ---")
print("Attempting to import Django settings module...")

try:
    # Set the DJANGO_SETTINGS_MODULE environment variable just like manage.py does
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lekkerbill.settings')

    # The critical import that is likely failing
    from django.conf import settings

    # If the import succeeds, we must access a setting to force it to be fully configured.
    # This will trigger any lazy-loading errors.
    _ = settings.SECRET_KEY

    print("✅ SUCCESS: Django settings module imported successfully.")

except Exception as e:
    print(f"❌ FATAL: Failed to import Django settings module.")
    print("--- TRACEBACK ---")
    import traceback
    # This will print the full traceback to standard output, which will appear in the deploy logs.
    traceback.print_exc()
    print("--- END TRACEBACK ---")
    # Exit with a non-zero status code to halt the release phase
    sys.exit(1)

print("--- SETTINGS IMPORT CHECK COMPLETE ---")
# F:/Python Apps/LekkerBill_Django_Clean/run_release_tasks.py
import os
import sys
import django
from django.core.management import call_command

# More verbose logging to pinpoint failures
print("--- [STEP 1/7] Release task script started.")

try:
    # Set up the Django environment
    print("--- [STEP 2/7] Setting DJANGO_SETTINGS_MODULE environment variable.")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lekkerbill.settings')
    print("--- [STEP 3/7] Initializing Django with django.setup().")
    django.setup()
    print("✅ [SUCCESS] Django initialized successfully.")

    # Run the migrate command
    print("\n--- [STEP 4/7] Calling 'migrate' command...")
    call_command('migrate', '--noinput')
    print("✅ [SUCCESS] Database migrations completed.")

    # Run the createsu command
    print("\n--- [STEP 5/7] Calling 'createsu' command...")
    call_command('createsu')
    print("✅ [SUCCESS] Superuser check completed.")

    print("\n--- [STEP 6/7] All tasks finished without raising an exception.")

except Exception as e:
    print(f"\n❌ [FATAL] An exception occurred during release tasks.")
    print(f"--- [ERROR TYPE]: {type(e).__name__}")
    print(f"--- [ERROR DETAILS]: {e}")
    print("--- [TRACEBACK] ---")
    import traceback
    traceback.print_exc()
    print("--- [END TRACEBACK] ---")
    # Exit with a non-zero status code to signal failure to the platform
    sys.exit(1)

print("\n--- [STEP 7/7] Script finished. ALL RELEASE TASKS COMPLETED SUCCESSFULLY ---")
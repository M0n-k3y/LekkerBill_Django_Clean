# F:/Python Apps/LekkerBill_Django_Clean/run_release_tasks.py
import os
import sys
import django
from django.core.management import call_command

print("--- UNIFIED RELEASE TASK RUNNER INITIATED ---")
print("Initializing Django...")

try:
    # Set up the Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lekkerbill.settings')
    django.setup()
    print("✅ Django initialized successfully.")

    # --- ✅ NEW DEBUGGING STEP ---
    print("\n--> DEBUG: Listing contents of the source static directory...")
    # The path inside the container will be /app/invoices/static
    source_static_dir = os.path.join(os.path.dirname(__file__), 'invoices', 'static')
    if os.path.exists(source_static_dir):
        print(f"Directory found: {source_static_dir}")
        for root, dirs, files in os.walk(source_static_dir):
            # To make the output cleaner, remove the base path
            relative_root = os.path.relpath(root, source_static_dir)
            if relative_root == '.':
                relative_root = ''
            print(f"  - Subdirectory: {relative_root}/")
            for filename in files:
                print(f"    - File: {os.path.join(relative_root, filename)}")
    else:
        print(f"❌❌❌ WARNING: Source static directory NOT FOUND at {source_static_dir}")
    print("--- END DEBUG ---")
    # --- END OF NEW DEBUGGING STEP ---

    # Run the collectstatic command
    print("\n--> Collecting static files...")
    # The --noinput flag is crucial for non-interactive environments
    call_command('collectstatic', '--noinput')
    print("✅ SUCCESS: Static files collected.")

    # Run the migrate command
    print("\n--> Running database migrations...")
    call_command('migrate')
    print("✅ SUCCESS: Database migrations completed.")

    # Run the createsu command
    print("\n--> Checking for/creating superuser...")
    call_command('createsu')
    print("✅ SUCCESS: Superuser check completed.")

except Exception as e:
    print(f"\n❌ FATAL: An exception occurred during release tasks.")
    print("--- TRACEBACK ---")
    import traceback
    traceback.print_exc()
    print("--- END TRACEBACK ---")
    sys.exit(1)

print("\n--- ALL RELEASE TASKS COMPLETED SUCCESSFULLY ---")
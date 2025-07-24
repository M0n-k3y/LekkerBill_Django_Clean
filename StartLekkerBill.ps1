# StartLekkerBill.ps1
# This script activates the virtual environment and starts the Django development server

# Activate the virtual environment
& "F:\Python Apps\LekkerBill_Django_Clean\venv\Scripts\Activate.ps1"

# Navigate to project folder (optional, just for clarity)
Set-Location -Path "F:\Python Apps\LekkerBill_Django_Clean"

# Start Django development server
python manage.py runserver

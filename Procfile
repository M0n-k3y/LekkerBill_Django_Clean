# F:/Python Apps/LekkerBill_Django_Clean/Procfile

release: python manage.py check_env && python manage.py migrate && python manage.py createsu
web: gunicorn lekkerbill.wsgi --bind 0.0.0.0:$PORT --log-level=debug
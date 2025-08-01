# F:/Python Apps/LekkerBill_Django_Clean/Procfile

release: python raw_check.py && python manage.py migrate && python manage.py createsu
web: gunicorn lekkerbill.wsgi --bind 0.0.0.0:$PORT --log-level=debug
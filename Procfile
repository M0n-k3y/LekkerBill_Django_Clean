# F:/Python Apps/LekkerBill_Django_Clean/Procfile

release: python manage.py collectstatic --noinput && python manage.py migrate && python manage.py createsu
web: python manage.py check && gunicorn lekkerbill.wsgi --bind 0.0.0.0:$PORT --log-level=debug
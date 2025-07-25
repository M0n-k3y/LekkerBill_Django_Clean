# Trigger re-deploy
release: python manage.py migrate && python manage.py createsu
web: gunicorn lekkerbill.wsgi --bind 0.0.0.0:$PORT
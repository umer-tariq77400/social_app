release: python manage.py tailwind build && python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: gunicorn config.wsgi:application
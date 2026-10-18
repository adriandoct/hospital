web: python manage.py migrate --noinput && python manage.py collectstatic --noinput && python init_system.py && gunicorn federated_project.wsgi:application

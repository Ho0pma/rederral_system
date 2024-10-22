#!/bin/bash

python manage.py migrate
python manage.py createsuperuser --noinput --username=root --email=test@mail.ru

exec gunicorn --bind 0.0.0.0:8000 web.wsgi:application
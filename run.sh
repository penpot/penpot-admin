#!/usr/bin/env bash

set -ex
python manage.py migrate
# exec python manage.py runserver 0.0.0.0:6063 --nostatic
exec gunicorn -w 3 -b 0.0.0.0:6063 penpot_admin.wsgi

#!/usr/bin/env bash

set -ex
python manage.py migrate
# exec python manage.py runserver 0.0.0.0:6065 --nostatic
exec gunicorn -w 3 -b 0.0.0.0:6065 penpot_admin.wsgi

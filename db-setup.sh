#!/usr/bin/env bash
python manage.py create-db
python manage.py db init
python manage.py db migrate
python manage.py create-admin
python manage.py create-data
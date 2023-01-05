#!/usr/bin/env bash
# exit on error
set -o errexit

poetry cache clear . --all -n
rm poetry.lock
poetry install

python manage.py collectstatic --no-input
python manage.py migrate
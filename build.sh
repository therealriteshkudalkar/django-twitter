#!/usr/bin/env bash
# exit on error
set -o errexit

poetry self update
poetry install

python manage.py collectstatic --no-input
python manage.py migrate
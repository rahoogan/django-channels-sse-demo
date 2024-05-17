#!/bin/bash
set -e

poetry run python manage.py makemigrations
poetry run python manage.py migrate
# poetry run gunicorn --reload $(find . -type f -name '*.html' -exec echo -n --reload-extra-file '{} ' \;  |xargs echo -n) -b 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker sse.asgi:application
poetry run uvicorn --host 0.0.0.0 --port 8000 --reload --reload-include "sse/events/templates/*" sse.asgi:application
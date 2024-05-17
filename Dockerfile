FROM python:3.11

ARG USER
ARG GROUP

WORKDIR /app

COPY --chown=${USER}:${GROUP} pyproject.toml README.md manage.py /app/

ENV PATH="${PATH}:~/.local/bin"

RUN pip install poetry && python -m poetry install

COPY --chown=${USER}:${GROUP} . /app

CMD poetry run python manage.py runserver

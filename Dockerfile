FROM python:3.8-slim-buster

ENV DJANGO_SUPERUSER_PASSWORD=password \
    DJANGO_SUPERUSER_USERNAME=admin \
    DJANGO_SUPERUSER_EMAIL=admin@localhost

WORKDIR /app
COPY . .

RUN pip install poetry
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi
ENTRYPOINT ["/app/entrypoint.sh"]
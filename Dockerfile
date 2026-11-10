# syntax=docker/dockerfile:1

FROM python:3.12-slim AS runtime
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_DEBUG=false

# gunicorn serves the app; the slim base has no compiler, and the pinned
# dependencies (pandas, numpy) publish manylinux wheels, so none is needed.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt gunicorn==23.0.0

COPY manage.py ./
COPY tourism_analyzer ./tourism_analyzer
COPY tourism_dashboard ./tourism_dashboard
COPY src ./src
COPY static ./static

# Collect static files at build time so the running container needs no write
# access to the image. A throwaway key is used because collectstatic reads
# settings but never signs anything.
RUN DJANGO_SECRET_KEY=build-time-only-not-used-at-runtime \
    DJANGO_DEBUG=true \
    python manage.py collectstatic --noinput

RUN useradd --create-home --shell /usr/sbin/nologin app \
    && chown -R app:app /app
USER app

EXPOSE 8000

# Binds all interfaces inside the container; the published port is the security
# boundary (see docker-compose.yml, which publishes to 127.0.0.1 only).
CMD ["gunicorn", "tourism_analyzer.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--timeout", "120", \
     "--access-logfile", "-"]

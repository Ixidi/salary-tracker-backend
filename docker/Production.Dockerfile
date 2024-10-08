FROM python:3.12.6

EXPOSE 80

ARG APP_VERSION
RUN test -n "$APP_VERSION" || (echo "APP_VERSION build-arg is required" && false)
ENV APP_VERSION=$APP_VERSION

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip  \
    && pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY test/ test/
COPY migrations/ migrations/
COPY alembic.ini alembic.ini

CMD [ "uvicorn", "--host", "0.0.0.0", "--port", "80", "youoweme.presentation.main:app" ]
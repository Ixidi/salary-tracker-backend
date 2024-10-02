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
COPY res/ res/
COPY migration/ migration/
COPY alembic.ini alembic.ini
COPY log_conf.yml log_conf.yml
COPY manager.py manager.py

CMD ["/bin/bash"]
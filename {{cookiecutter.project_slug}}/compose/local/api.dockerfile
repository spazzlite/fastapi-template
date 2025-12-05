FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=Etc/UTC \
    LANG=C.UTF-8

WORKDIR /code

COPY ./src/requirements /code/requirements

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip \
    && pip install -r /code/requirements/local.txt

COPY ./scripts/prestart.sh /
COPY ./scripts/start-reload.sh /

RUN chmod +x /prestart.sh
RUN chmod +x /start-reload.sh

COPY ./src /code/src

CMD ["/start-reload.sh"]

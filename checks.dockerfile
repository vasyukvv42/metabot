FROM python:3.8-slim-buster

WORKDIR /app

ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV MYPYPATH "${MYPYPATH}:/app"

COPY requirements.txt requirements-dev.txt /app/
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt --no-deps --no-cache-dir && \
    pip3 install -r requirements-dev.txt --no-deps --no-cache-dir

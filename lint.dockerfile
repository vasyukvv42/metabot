FROM python:3.8-slim-buster

WORKDIR /app

ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV MYPYPATH "${MYPYPATH}:/app"

COPY requirements-lint.txt /app/
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements-lint.txt --no-deps --no-cache-dir

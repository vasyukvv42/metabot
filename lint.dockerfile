FROM python:3.8-slim-buster

WORKDIR /app

ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV MYPYPATH "${MYPYPATH}:/app"

COPY lint-requirements.txt .flake8 mypy.ini /app/
RUN pip3 install --upgrade pip && \
    pip3 install -r lint-requirements.txt --no-deps --no-cache-dir

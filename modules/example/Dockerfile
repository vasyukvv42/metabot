FROM python:3.8-slim-buster as dev

WORKDIR /app

ENV PYTHONPATH "${PYTHONPATH}:/app"

RUN pip install --upgrade pip \
 && pip install uvicorn fastapi-metabot==0.0.6 --no-cache-dir

COPY . .
EXPOSE 8000

CMD ["uvicorn", "example:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.8-slim-buster as dev

WORKDIR /app

ENV PYTHONPATH "${PYTHONPATH}:/app"

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install -r requirements.txt --no-deps --no-cache-dir

COPY vacations ./vacations
EXPOSE 8000

CMD ["uvicorn", "vacations.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]


FROM dev AS deploy

CMD ["uvicorn", "vacations.main:app", "--host", "0.0.0.0", "--port", "8000"]

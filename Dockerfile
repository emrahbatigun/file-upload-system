# Use Python 3.10 Alpine as the base image
FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apk update && \
    apk add --no-cache gcc musl-dev linux-headers mariadb-dev

COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /requirements.txt

COPY . /app
WORKDIR /app

EXPOSE 8000

CMD ["sh", "-c", "python3 manage.py migrate && python3 manage.py collectstatic --noinput && python3 manage.py runserver 0.0.0.0:8000"]

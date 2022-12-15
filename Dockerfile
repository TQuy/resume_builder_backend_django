# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /backend
COPY ./requirements.production.txt /backend/
RUN pip install -r requirements.production.txt
COPY . /backend/
RUN python manage.py makemigrations
RUN python manage.py migrate
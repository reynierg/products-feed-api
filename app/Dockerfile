FROM python:3.11.2-slim-buster

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Keep the files that frequently change towards the end of the Dockerfile to harness
# layers' caching and minimize cache invalidation.
COPY . .

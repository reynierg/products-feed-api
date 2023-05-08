FROM python:3.11.2-slim-buster

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive \
     apt-get -y --no-install-recommends install netcat gcc postgresql \
  && apt-get -y autoremove \
  && apt-get clean autoclean \
  && rm -rf /var/lib/apt/lists/{apt,dpkg,cache,log} /tmp/* /var/tmp/*

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# Keep the files that frequently change towards the end of the Dockerfile to harness
# layers' caching and minimize cache invalidation.
COPY . .

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
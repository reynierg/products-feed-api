#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for PostgreSQL database..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      echo "Database unavailable, waiting 1s..."
      sleep 1
    done

    echo "PostgreSQL db is ready!"
fi

python manage.py flush --no-input
python manage.py migrate

exec "$@"

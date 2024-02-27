FROM python:3.9

WORKDIR /app

RUN pip install gunicorn==20.1.0

COPY . .

RUN pip install -r /app/requirements.txt --no-cache-dir

RUN python manage.py collectstatic --no-input

CMD ["gunicorn",  "--bind", "0.0.0.0:8000", "foodgram.wsgi:application"]
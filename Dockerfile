FROM python:3.7
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD gunicorn --bind 0.0.0.0:5000 wsgi:app
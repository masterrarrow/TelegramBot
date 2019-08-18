FROM python:3
MAINTAINER masterarrow "masterarrows@gmail.com"
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
COPY requirements.pip /app/
RUN pip install -r requirements.pip
COPY . /app/
CMD python manage.py collectstatic --no-input;python manage.py migrate

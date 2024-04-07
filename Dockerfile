FROM python:3.8

COPY ./requirements /requirements
RUN pip install --upgrade pip
RUN pip install -r requirements/base.txt
RUN pip install -r requirements/dev.txt
RUN pip install -r requirements/tests.txt

RUN apt update \
    && apt install -v libpq-dev gcc

RUN pip install psycopg2

WORKDIR /code
COPY . /code/

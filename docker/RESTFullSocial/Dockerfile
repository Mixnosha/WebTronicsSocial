FROM python:3.10.6-alpine

RUN mkdir /RESTFullSocial

WORKDIR /RESTFullSocial

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --no-cache-dir --upgrade pip

COPY RESTFullSocial /RESTFullSocial


RUN pip install --no-cache-dir --upgrade -r requirements.txt



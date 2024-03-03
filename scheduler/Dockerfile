FROM python:3.10-slim

RUN apt-get update 

WORKDIR  /app

COPY scheduler .
COPY config.toml .
COPY requirements.txt .

RUN pip install -r requirements.txt
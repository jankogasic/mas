# Use official Python slim image as the base
FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y curl build-essential htop && \
    apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip install -Ur requirements.txt

COPY . .

ENV USERNAME jnk
ENV LOGLEVEL CRITICAL
ENV METAFLOW_HOME /etc/metaflowconfig

# RUN python -m spacy download en_core_web_sm

COPY .metaflowconfig/config.json $METAFLOW_HOME/config.json

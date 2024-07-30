# Use official Python slim image as the base
FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean

# Set the working directory in the container
WORKDIR /app

COPY . .

ENV USERNAME jnk
ENV METAFLOW_HOME /etc/metaflowconfig

# Install the required packages
RUN pip3 install -Ur requirements.txt

# Copy the rest of the application code
COPY .metaflowconfig/config.json $METAFLOW_HOME/config.json

# Use official Python slim image as the base
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

ENV USERNAME jnk

# Install the required packages
RUN pip3 install -Ur requirements.txt

# Copy the rest of the application code
COPY . .
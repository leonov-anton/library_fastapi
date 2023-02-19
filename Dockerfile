# Pull base image
FROM python:3.8

# Set environment varibles
ENV PYTHONUNBUFFERED=1

RUN mkdir /code
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /code/

EXPOSE 8000

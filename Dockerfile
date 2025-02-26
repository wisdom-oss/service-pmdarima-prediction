# syntax=docker/dockerfile:1
FROM python:3.13-bookworm
WORKDIR /service-water-prediction

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libopenblas-dev \
    liblapack-dev

COPY --link . /service-water-prediction

RUN pip install --upgrade pip setuptools wheel
RUN pip install pmdarima
RUN pip install -r requirements.txt

ENV API_PREFIX=/waterdemand
ENV DEVICE_PREFIX=urn:ngsi-ld:Device:
ENV STARTING_DATE_SMARTMETER=2021-05-26T00:00:00
EXPOSE 8080
CMD flask run --host 0.0.0.0 --port 8000

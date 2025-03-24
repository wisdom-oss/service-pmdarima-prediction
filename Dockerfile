# Use an official Python runtime as a parent image
FROM python:3.12.9-bookworm

# Set the working directory in the container
WORKDIR /service-water-demand-prediction

# Install system dependencies (build-essential, gcc, etc.)
RUN apt-get update
# && apt-get install -y python3-dev gcc

RUN pip install --upgrade pip

# Copy your requirements.txt into the container
COPY requirements.txt /service-water-demand-prediction/

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of your application code into the container
COPY . /service-water-demand-prediction/

# setting up ENV variables
ENV DEVICE_PREFIX=urn:ngsi-ld:Device:
ENV STARTING_DATE_SMARTMETER=2021-05-26T00:00:00
ENV FILE_PATH_TRAINED_MODELS=files/trained_models/
ENV FILE_PATH_EXAMPLE_DATA=files/smartmeterdata/
ENV FILE_PATH_RESULTS=files/results/
ENV EXAMPLE_META_DATA=example_pm_meta.json
ENV EXAMPLE_DATA=example_pm_measurements.json
ENV DATETIME_STANDARD_FORMAT="%d.%m.%y %H:%M"
ENV ALLOW_DUPLICATE_MODELS=True

EXPOSE 8080
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]

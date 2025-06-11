# Use an official Python runtime as a parent image
FROM python:3.12.9-bookworm

# Set the working directory in the container
WORKDIR /service-water-demand-prediction

# Copy your requirements.txt into the container
COPY requirements.txt /service-water-demand-prediction/

# Install updates
RUN apt-get update
RUN apt-get install

# upgrade pip and install requirements
RUN pip install --upgrade pip && pip install -r requirements.txt

# installation over standard not working (may over requirements)
# pip install "psycopg[binary]"

# Copy the rest of your application code into the container
COPY . /service-water-demand-prediction/

# setting up ENV variables
ENV FLASK_APP=app.py
ENV DWD_API_V1=https://wisdom-demo.uol.de/api/dwd/v1
ENV WEATHER_STATION=/00691

EXPOSE 8090
CMD ["flask", "run", "--host=0.0.0.0", "--port=8090"]

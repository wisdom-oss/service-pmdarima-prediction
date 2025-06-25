# Use an official Python runtime as a parent image
FROM ghcr.io/astral-sh/uv:python3.12-bookworm

# Set the working directory in the container
WORKDIR /service-water-demand-prediction

# Copy the rest of your application code into the container
COPY . /service-water-demand-prediction/

# Sync uv project in new environment
RUN uv sync --locked

EXPOSE 8090

CMD ["uv", "run", "app.py"]
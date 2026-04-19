# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the actual script
COPY log_processor.py /app/

# Create a directory to hold the state file
RUN mkdir -p /app/data

# Expose the Prometheus metrics port
EXPOSE 8000

# Set environment variables for the log processor
# These can be overridden in the Kubernetes deployment or Docker run command
ENV LOG_FILE_PATH=/var/log/apache2/access.log
ENV STATE_FILE_PATH=/app/data/state.json
ENV METRICS_PORT=8000

# Run the Python script when the container launches
CMD ["python", "-u", "log_processor.py"]

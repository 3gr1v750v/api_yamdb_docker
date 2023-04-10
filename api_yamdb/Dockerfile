# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY api_yamdb/requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the application code into the container at /app
COPY api_yamdb/ /app

# Start the Django application using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "api_yamdb.wsgi:application"]

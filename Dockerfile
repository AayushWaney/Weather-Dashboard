# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose port 10000 (Render's default port)
EXPOSE 10000

# Run gunicorn, changing to the weather_app directory first
CMD ["gunicorn", "--chdir", "weather_app", "app:app", "--bind", "0.0.0.0:10000"]
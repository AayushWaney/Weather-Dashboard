# Use official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install them securely
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the Flask port
EXPOSE 5000

# Command to run the application
CMD ["flask", "run", "--host=0.0.0.0"]
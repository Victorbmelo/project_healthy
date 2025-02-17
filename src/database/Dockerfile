# Base image: Python 3.10 slim version
FROM python:3.10-slim

# Set the working directory
WORKDIR /app
COPY . /app

# Set the PYTHONPATH to include the 'src' folder
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Expose the port used by the application (default 8080)
EXPOSE 8080

# Command to start the application
CMD ["python", "src/database/db_connector.py"]


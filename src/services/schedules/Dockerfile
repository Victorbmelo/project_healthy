# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app
COPY . /app

# Set the PYTHONPATH to include the 'src' folder
ENV PYTHONPATH=/app/src:$PYTHONPATH
# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Define the default command to run the service
CMD ["python", "src/services/schedules/schedule_service.py"]

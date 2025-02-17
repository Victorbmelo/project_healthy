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

# Expose the port on which CherryPy will run
EXPOSE 8081

# Define the default command to run the server.
CMD ["python", "src/services/thingspeak/thingspeak_adapter.py"]

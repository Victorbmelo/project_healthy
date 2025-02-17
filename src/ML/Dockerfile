# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app
# Copy the application code and model files
COPY . /app

# Copy the requirements file and install dependencies
COPY requirements.txt ./

# Set the PYTHONPATH to include the 'src' folder
ENV PYTHONPATH=/app/src:$PYTHONPATH

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Expose the port on which the CherryPy dashboard listens (dashboard_socket=8082)
EXPOSE 8082

# Define the default command to run your service
CMD ["python", "src/ML/Project_ML_analysis.py"]

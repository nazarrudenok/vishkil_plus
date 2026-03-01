# Use a base Python image
FROM python:3.12-slim

# Set the working directory
WORKDIR /

# Copy your application code
COPY . /

# Install dependencies
RUN pip install -r requirements.txt

# Define the command to run your application
CMD ["python", "main.py"]

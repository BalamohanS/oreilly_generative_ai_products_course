FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
EXPOSE 8000
WORKDIR /app

# Copy requirements from host, to docker container in /app
COPY app/requirements.txt .

# Copy everything from ./src directory to /app in the container
COPY ./app .

# Install the requirements
RUN pip install -r requirements.txt

# Run the application in the port 8000
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "main:app"]
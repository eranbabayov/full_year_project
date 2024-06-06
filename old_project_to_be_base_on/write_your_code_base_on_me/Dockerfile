FROM python:3.10.10

# Set the working directory in the container to /app
WORKDIR /app
ADD . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD ["python", "backend.py"]
# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the application code to the container
COPY requirements.txt /app
RUN pip install -r requirements.txt --no-cache-dir
COPY . /code

# Set environment variables
ENV SQLALCHEMY_DATABASE_URI="mysql+pymysql://$DB_USER:$DB_PASS@$DB_HOST:$DB_PORT/$DB_NAME"
ENV SQLALCHEMY_TRACK_MODIFICATIONS=False
ENV JWT_SECRET_KEY=secret
ENV FLASK_APP=app
# Expose port 5000 for the Flask app to listen on
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "app.py"]

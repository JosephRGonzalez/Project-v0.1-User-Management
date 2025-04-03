# Use official Python image as a base
FROM python:3.11

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Copy the project files into the container
COPY . /app/

# Install system dependencies (e.g., for Pillow and database support)
RUN apt-get update && apt-get install -y \
    libpq-dev gcc python3-dev musl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port 8000 (default Django port)
EXPOSE 8000

# Command to run the app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "User_Management_System.wsgi:application"]


# Run these commands:
# docker build -t thunder-bay
# docker run -p 8000:8000 my-django-app
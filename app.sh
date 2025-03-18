#!/bin/bash

echo "Starting Resume Analyzer Application..."

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Start the Django development server
echo "Starting the Django server..."
python manage.py runserver 0.0.0.0:8000

echo "Resume Analyzer is running at http://127.0.0.1:8000/"

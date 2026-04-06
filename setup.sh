#!/bin/bash
set -e

echo "Starting setup for Django Real-Time Chat Application"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment"
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing requirements"
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating environment file"
    cp .env.example .env
fi

echo "Running migrations"
python manage.py migrate

echo "Setup finished"
echo "Run the app with: python manage.py runserver"

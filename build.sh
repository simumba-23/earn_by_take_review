#!/usr/bin/env bash
# Exit on error
set -o errexit

# Navigate to the project directory where manage.py is located
cd earn_app

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Upgrade pip and install required packages from the correct path
pip install --upgrade pip
pip install -r ../requirements.txt

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

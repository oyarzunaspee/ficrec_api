#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Apply any outstanding database migrations
python manage.py makemigrations authentication
python manage.py makemigrations user_profile
python manage.py makemigrations public
python manage.py migrate authentication
python manage.py migrate user_profile
python manage.py migrate public
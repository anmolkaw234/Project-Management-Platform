@echo off

REM Create a virtual environment
python -m venv .venv

REM Activate the virtual environment
call .venv\Scripts\activate

REM Install the dependencies
pip install -r requirements.txt

REM Make migrations
python manage.py makemigrations

REM Apply migrations
python manage.py migrate

REM Run the development server
python manage.py runserver 0.0.0.0:7275
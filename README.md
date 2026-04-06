<<<<<<< HEAD
# Django Real-Time Chat Application

Topic-based chat room web application where users can register, create rooms, and discuss in real time, built end-to-end with Django backend and vanilla JavaScript frontend.

## Project Summary

Implemented full user authentication, room-based messaging with topic categorisation, and session management using Django’s built-in auth framework and ORM.

Built a responsive frontend using HTML, CSS, and vanilla JavaScript, handling dynamic UI updates without a heavy JavaScript framework.

Deployed and tested the application end-to-end, validating concurrent user sessions, cross-browser compatibility, and message persistence across room sessions.

## Tech Stack

Django
Python
JavaScript
HTML & CSS
PostgreSQL
REST APIs

## How to Run

1. Open a terminal in the project folder.
2. Create a virtual environment.
3. Activate the virtual environment.
4. Install the requirements.
5. Run the migrations.
6. Start the server.

macOS or Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.

## Notes

For local development, the project uses SQLite by default.

If you want to use PostgreSQL, set a DATABASE_URL value in the environment.
=======
# django-real-time-chat-application
>>>>>>> a8b67db1742ebf74fe23b103584b6b79fd3276e2

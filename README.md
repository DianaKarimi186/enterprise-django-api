# Enterprise Django API

A production-ready Django REST Framework backend for managing products in an e-commerce environment.

## Features

- Product CRUD API
- Category management
- Django REST Framework serializers
- HTML Dashboard
- Celery background tasks
- Django Signals
- Unit Tests
- SQLite database
- GitHub version control

## Tech Stack

- Python 3.13
- Django
- Django REST Framework
- Celery
- SQLite
- HTML
- Git & GitHub

## Project Structure

```
ecommerce_backend/
│
├── ecommerce_backend/
│   ├── settings.py
│   ├── urls.py
│   └── celery.py
│
├── products/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   ├── tasks.py
│   ├── signals.py
│   └── templates/
│
├── manage.py
└── db.sqlite3
```

## Installation

Clone the repository

```bash
git clone https://github.com/DianaKarimi186/enterprise-django-api.git
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run migrations

```bash
python manage.py migrate
```

Start the development server

```bash
python manage.py runserver
```

Visit

```
http://127.0.0.1:8000/
```

## Future Improvements

- JWT Authentication
- Swagger Documentation
- Docker Support
- PostgreSQL
- GitHub Actions
- Deployment on Render

## Author

**Diana Karimi**

GitHub:
https://github.com/DianaKarimi186
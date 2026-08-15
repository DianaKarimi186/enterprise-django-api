# Enterprise Inventory Management API

A Django-based inventory management system that I built to practice and demonstrate real-world backend development.

The project started as an e-commerce API and has gradually grown into a more complete inventory system. It currently includes user authentication, product management, ownership controls, search and filtering, a browser-based dashboard, background processing with Celery, Redis caching, and Docker-based development.

The main goal of the project is to bring together the backend concepts I have been learning into one working application rather than building separate small examples.

---

## What the Project Does

The system allows an authenticated user to manage their inventory through both a REST API and a simple web dashboard.

Currently, a user can:

- Create an account
- Log in using JWT authentication
- Create products
- View their products
- Edit products
- Delete products
- Search inventory
- Filter products by category
- Sort products by price, stock, or creation date
- Upload product images
- Process longer-running tasks in the background
- Check the status of background tasks
- Access API documentation

One important part of the project is product ownership. Users should only be able to manage products that belong to their own account.

---

## Main Technologies

### Backend

- Python
- Django
- Django REST Framework
- PostgreSQL
- Django Filters
- Simple JWT

### Background Processing

- Celery
- Redis

### Frontend

- Django Templates
- HTML
- Tailwind CSS
- HTMX
- JavaScript

### Development and Documentation

- Docker
- Docker Compose
- pytest
- pytest-django
- drf-spectacular
- OpenAPI

---

## Project Structure

The project is divided into Django applications so that each part of the system has its own responsibility.

```text
Project1/
│
├── accounts/
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
│   ├── templates/
│   └── tests/
│
├── products/
│   ├── models.py
│   ├── serializers.py
│   ├── permissions.py
│   ├── signals.py
│   ├── tasks.py
│   ├── urls.py
│   ├── views.py
│   ├── templates/
│   └── tests/
│
├── cart/
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── views.py
│   └── tests/
│
├── orders/
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── views.py
│   └── tests/
│
├── payments/
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── views.py
│   └── tests/
│
├── ecommerce_backend/
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   ├── exceptions.py
│   ├── asgi.py
│   └── wsgi.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── schema.yml
├── manage.py
└── README.md
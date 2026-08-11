# Enterprise Django API

A production-oriented e-commerce backend built with **Django REST Framework**, providing APIs for authentication, product management, shopping carts, orders, and payments. The project also includes JWT authentication, PostgreSQL, Redis, Celery background processing, automated testing, and OpenAPI documentation.

## Features

* JWT authentication and token refresh
* User authentication APIs
* Product CRUD API
* Category management
* Shopping cart management
* Add, remove, and update cart items
* Automatic cart totals and item subtotals
* Order creation and management
* Payment processing API
* Celery background tasks
* Redis message broker
* Django signals
* PostgreSQL database
* Automated API and application tests
* OpenAPI schema generation
* Swagger UI documentation
* ReDoc API documentation
* Environment-based configuration using `.env`
* GitHub version control

## Tech Stack

* **Python 3.13**
* **Django 6.0.6**
* **Django REST Framework**
* **Simple JWT**
* **PostgreSQL**
* **Celery 5.6.3**
* **Redis**
* **drf-spectacular**
* **python-dotenv**
* **pytest**
* **Git & GitHub**

## Project Structure

```text
enterprise-django-api/
│
├── accounts/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests/
│
├── products/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── tasks.py
│   ├── signals.py
│   └── tests/
│
├── cart/
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── views.py
│   ├── urls.py
│   └── tests/
│
├── orders/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests/
│
├── payments/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests/
│
├── ecommerce_backend/
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   ├── asgi.py
│   └── wsgi.py
│
├── schema.yml
├── manage.py
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md
```

## API Endpoints

### Authentication

```text
POST /api/token/
POST /api/token/refresh/
```

### Accounts

```text
/api/accounts/
```

### Products

```text
/api/products/
```

### Cart

```text
GET    /api/cart/
POST   /api/cart/add/<product_id>/
PATCH  /api/cart/update/<product_id>/
DELETE /api/cart/remove/<product_id>/
```

### Orders

```text
/api/orders/
```

### Payments

```text
/api/payments/
```

## API Documentation

Interactive API documentation is available through Swagger UI and ReDoc.

### Swagger UI

```text
http://127.0.0.1:8000/api/docs/
```

### ReDoc

```text
http://127.0.0.1:8000/api/redoc/
```

### OpenAPI Schema

```text
http://127.0.0.1:8000/api/schema/
```

The generated OpenAPI specification is also available in:

```text
schema.yml
```

## Background Processing

The project uses **Celery with Redis** to execute background tasks asynchronously.

The current implementation includes a background processing task in:

```text
products/tasks.py
```

Example task:

```python
simulate_heavy_background_job()
```

Start the Celery worker with:

```bash
celery -A ecommerce_backend.celery:app worker -l info --pool=solo
```

Redis must be running before starting the Celery worker.

## Environment Configuration

Sensitive configuration is stored in environment variables rather than committed directly to Git.

Create a `.env` file in the project root based on `.env.example`.

Example:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True

DB_NAME=enterprise_api
DB_USER=enterprise_user
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://127.0.0.1:6379
```

The `.env` file should **never be committed to Git**.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/DianaKarimi186/enterprise-django-api.git
cd enterprise-django-api
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

Windows:

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create `.env` using `.env.example` as a template.

### 6. Run database migrations

```bash
python manage.py migrate
```

### 7. Start the Django development server

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

### 8. Start Celery

In a separate terminal:

```bash
celery -A ecommerce_backend.celery:app worker -l info --pool=solo
```

## Running Tests

The project uses **pytest** for automated testing.

Run the complete test suite:

```bash
pytest
```

Current test status:

```text
31 passed
```

Run a specific test file:

```bash
pytest products/tests/test_tasks.py -v
```

## System Checks

Run Django's system checks with:

```bash
python manage.py check
```

## Generate API Schema

To regenerate the OpenAPI schema:

```bash
python manage.py spectacular --file schema.yml --validate
```

## GitHub

Repository:

https://github.com/DianaKarimi186/enterprise-django-api

## Future Improvements

* Docker and Docker Compose support
* GitHub Actions CI/CD
* Production deployment
* API rate limiting
* Advanced permissions and roles
* Email notifications
* Improved payment integration
* Production monitoring and logging
* Automated deployment pipeline

## Author

**Diana Karimi**

GitHub:

https://github.com/DianaKarimi186

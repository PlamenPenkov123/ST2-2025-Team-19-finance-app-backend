# Finance App Backend

This is the backend for the Finance App. Follow the instructions below to set up and run the project.

## Prerequisites

- Python 3.x installed
- `pip` installed

## Setup

1. **Clone the repository**
    ```bash
    git clone <repository-url>
    cd finance-app-api
    ```

2. **Create and activate a virtual environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install requirements**
    ```bash
    pip install -r requirements.txt
    ```

## Database Migrations

Run the following command to apply migrations:

```bash
python manage.py migrate
```

## Running the Project

Start the development server:

```bash
python manage.py runserver
```

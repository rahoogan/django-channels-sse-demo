# Django Notifications with Channels and SSE

This is a simple example app to demonstrate how to setup real-time notifications using Django Channels and Server Sent Events. Full write up can be found here

## Getting Started

### Option 1: with docker

```bash
docker compose up
```

### Option 2: without docker

1. Install poetry and dependencies

    ```
    pip install poetry
    poetry install
    ```

2. Run!

    ```bash
    python manage.py migrate
    poetry run uvicorn --host 0.0.0.0 --port 8000 --reload --reload-include "sse/events/templates/*" sse.asgi:application
    ```
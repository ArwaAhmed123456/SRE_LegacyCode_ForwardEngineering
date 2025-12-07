"""
ASGI config for POS project.

This file exposes the ASGI callable used for asynchronous servers such as Uvicorn or Daphne.
It also allows plugging in WebSockets or other async-compatible communication layers in the future.

For deployment details, see:
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# Ensure settings module is loaded
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos.settings')

# Main ASGI application entry point
application = get_asgi_application()

from task.settings.base import *

import os

# CONFIGURATION
# ------------------------------------------------------------------------------

DEBUG = True  # note: IT'S TRUE TO NOT SET AN NGINX FOR static FILES
SECRET_KEY = os.environ.get("SECRET_KEY")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
        "PORT": int(os.environ.get("DB_PORT")),
        "ATOMIC_REQUESTS": True,
    }
}

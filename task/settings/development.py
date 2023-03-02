from task.settings.base import *

import os

# CONFIGURATION
# ------------------------------------------------------------------------------

DEBUG = True
SECRET_KEY = os.environ.get("SECRET_KEY", "YOUR-AWESOME-SECRET-KEY")

# PASSWORD VALIDATION
# ------------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    # NO VALIDATION FOR DEVELOPMENT
]

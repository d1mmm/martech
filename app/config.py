import logging
import os
import bcrypt

JWT_SECRET = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2Mj"
              "M5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")
KEY = bcrypt.gensalt()
ALGORITHM = "HS256"

try:
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("Environment variable DATABASE_URL is not set or is empty")
except ValueError as v:
    logging.error(f"Environment variable is not set, {v}")
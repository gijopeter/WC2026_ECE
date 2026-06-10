import hashlib

ADMIN_PASSWORD_HASH = hashlib.sha256("12".encode()).hexdigest()
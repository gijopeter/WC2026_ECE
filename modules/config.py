import hashlib

ADMIN_PASSWORD_HASH = hashlib.sha256("Admin4321".encode()).hexdigest()
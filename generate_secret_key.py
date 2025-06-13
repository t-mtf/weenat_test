import secrets
import string

punctuation = "!@%_-+.:,"
chars = string.ascii_letters + string.digits + punctuation

secret_key = "".join(secrets.choice(chars) for _ in range(50))
print(secret_key)

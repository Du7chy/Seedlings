import secrets

secret_key = secrets.token_hex(32) # Generate key
print(secret_key)
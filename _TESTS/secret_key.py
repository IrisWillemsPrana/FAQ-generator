import secrets

# Genereer een veilige secret key van 24 bytes (192 bits)
secret_key = secrets.token_hex(24)
print(secret_key)
#!/usr/bin/env python3
"""Generate a secure secret key for Flask"""
import secrets

if __name__ == '__main__':
    secret_key = secrets.token_hex(32)
    print(secret_key)
    print(f"\nAdd this to Railway as environment variable:")
    print(f"SECRET_KEY={secret_key}")


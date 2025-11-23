"""
Utility script to generate password hash for authentication.
Run this to create a password hash for your Streamlit secrets.
"""

import hashlib
import getpass

def hash_password(password: str) -> str:
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

if __name__ == "__main__":
    print("=" * 60)
    print("Island Harvest Hub - Password Hash Generator")
    print("=" * 60)
    print()
    
    username = input("Enter username (default: admin): ").strip() or "admin"
    password = getpass.getpass("Enter password: ")
    
    if not password:
        print("Error: Password cannot be empty!")
        exit(1)
    
    password_hash = hash_password(password)
    
    print()
    print("=" * 60)
    print("Add this to your Streamlit Cloud Secrets:")
    print("=" * 60)
    print()
    print("[auth]")
    print(f'username = "{username}"')
    print(f'password_hash = "{password_hash}"')
    print()
    print("=" * 60)
    print("Or set as environment variables:")
    print("=" * 60)
    print()
    print(f'APP_USERNAME="{username}"')
    print(f'APP_PASSWORD_HASH="{password_hash}"')
    print()
    print("=" * 60)


"""Quick password hash generator for Island Harvest Hub authentication."""

import hashlib

# CHANGE THIS PASSWORD!
PASSWORD = "Admin123!"  # ⚠️ Change this to your desired password

def hash_password(password: str) -> str:
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

if __name__ == "__main__":
    print("=" * 70)
    print("Island Harvest Hub - Authentication Hash Generator")
    print("=" * 70)
    print()
    print(f"Password: {PASSWORD}")
    print()
    
    password_hash = hash_password(PASSWORD)
    
    print("=" * 70)
    print("COPY THIS TO STREAMLIT CLOUD SECRETS:")
    print("=" * 70)
    print()
    print("[auth]")
    print('username = "admin"')
    print(f'password_hash = "{password_hash}"')
    print()
    print("=" * 70)
    print()
    print("Steps:")
    print("1. Go to your Streamlit Cloud app")
    print("2. Click 'Manage app' → 'Settings' → 'Secrets'")
    print("3. Paste the [auth] section above")
    print("4. Save and the app will auto-redeploy")
    print("5. Login with username: admin, password:", PASSWORD)
    print()
    print("=" * 70)


# Authentication Setup Guide

## 🔐 Overview

The Island Harvest Hub application now includes simple password-based authentication to protect your data on Streamlit Cloud.

## 🚀 Quick Setup

### Step 1: Generate Password Hash

Run the password hash generator:

```bash
cd island_harvest_hub
python generate_password_hash.py
```

This will prompt you for:
- Username (default: `admin`)
- Password

It will output the hash that you need to add to Streamlit Cloud secrets.

### Step 2: Configure Streamlit Cloud Secrets

1. Go to your Streamlit Cloud app settings
2. Navigate to **Settings → Secrets**
3. Add the following:

```toml
[auth]
username = "admin"
password_hash = "<generated_hash_from_step_1>"
```

### Step 3: Alternative - Environment Variables

If you prefer environment variables, set:

```
APP_USERNAME=admin
APP_PASSWORD_HASH=<generated_hash>
```

## 🔒 Security Features

- **Password Hashing**: Passwords are hashed using SHA256
- **Session Management**: Authentication state persists during the session
- **Page Protection**: All pages require authentication
- **Secure Storage**: Credentials stored in Streamlit secrets (encrypted)

## 📝 Default Behavior

- **No credentials set**: App shows setup instructions and allows temporary access (setup mode)
- **Credentials set**: App requires login before accessing any content
- **Logout**: Available in sidebar, clears session state

## 🛠️ Local Development

For local development, you can:

1. **Use .env file** (not recommended for production):
   ```
   APP_USERNAME=admin
   APP_PASSWORD_HASH=<your_hash>
   ```

2. **Or create `.streamlit/secrets.toml`** (for local testing):
   ```toml
   [auth]
   username = "admin"
   password_hash = "<your_hash>"
   ```

   **⚠️ Important**: Add `.streamlit/secrets.toml` to `.gitignore` to avoid committing credentials!

## 🔄 Changing Password

1. Run `generate_password_hash.py` with new password
2. Update Streamlit Cloud secrets with new hash
3. Redeploy app (or wait for auto-redeploy)

## ⚠️ Important Security Notes

1. **Never commit passwords or hashes to Git**
2. **Use strong passwords** (minimum 8 characters, mix of letters, numbers, symbols)
3. **Rotate passwords regularly** for production use
4. **Single user only**: Current implementation supports one user account
5. **For multi-user**: Consider upgrading to a more robust authentication system

## 🚨 Troubleshooting

### "No password configured" warning
- **Solution**: Add credentials to Streamlit Cloud secrets as shown above

### Can't login after setting credentials
- **Check**: Password hash is correct (no extra spaces)
- **Check**: Username matches exactly (case-sensitive)
- **Solution**: Regenerate hash and update secrets

### Authentication not working on pages
- **Check**: All page files have authentication checks
- **Solution**: Ensure `from app.utils.auth import check_password, login` is imported

## 📚 Code Structure

- **Authentication Module**: `island_harvest_hub/app/utils/auth.py`
- **Password Generator**: `island_harvest_hub/generate_password_hash.py`
- **Protected Pages**: All pages in `island_harvest_hub/pages/` require authentication

## 🔐 For Production

For production deployments, consider:

1. **Multi-user support** with user database
2. **Role-based access control** (RBAC)
3. **OAuth integration** (Google, GitHub, etc.)
4. **Two-factor authentication** (2FA)
5. **Password complexity requirements**
6. **Session timeout** and automatic logout
7. **Audit logging** of login attempts

---

**Current Implementation**: Simple single-user password authentication
**Security Level**: Basic protection suitable for small teams/internal use


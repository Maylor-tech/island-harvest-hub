# Streamlit Cloud Deployment Guide

## ✅ Completed Steps

1. **Git Repository Initialized**
   - ✅ Repository initialized
   - ✅ Initial commit completed
   - ✅ All files committed

2. **Requirements File**
   - ✅ Root-level `requirements.txt` created
   - ✅ All dependencies listed (streamlit, sqlalchemy, pandas, plotly, etc.)

3. **Documentation**
   - ✅ Root-level `README.md` created with deployment instructions
   - ✅ Includes Streamlit Cloud setup steps

4. **Configuration**
   - ✅ `.gitignore` exists and properly configured
   - ✅ `.streamlit/config.toml` exists

---

## 🚀 Next Steps for Streamlit Cloud Deployment

### Step 1: Push to GitHub

1. **Create a GitHub repository:**
   ```bash
   # On GitHub, create a new repository named "island-harvest-enterprise"
   ```

2. **Add remote and push:**
   ```bash
   cd C:\Users\18023\island-harvest-enterprise
   git remote add origin https://github.com/YOUR_USERNAME/island-harvest-enterprise.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud:**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

2. **Create New App:**
   - Click "New app"
   - Select your repository: `island-harvest-enterprise`
   - Set **Main file path**: `island_harvest_hub/main.py`
   - Click "Deploy"

### Step 3: Configure Secrets

In Streamlit Cloud app settings → Secrets, add:

```toml
[secrets]
ANTHROPIC_API_KEY = "your_api_key_here"
DATABASE_URL = "sqlite:///island_harvest_hub.db"
```

**Note:** For production, consider using a cloud database (PostgreSQL) instead of SQLite.

### Step 4: Database Initialization

The app will need to initialize the database on first run. You have two options:

**Option A: Auto-initialization (Recommended)**
Add this to `island_harvest_hub/main.py` at the top (after imports):

```python
# Auto-initialize database if it doesn't exist
from pathlib import Path
from app.database.config import init_db, DATABASE_PATH

if not Path(DATABASE_PATH).exists():
    st.info("🔄 Initializing database...")
    init_db()
    st.success("✅ Database initialized!")
    st.rerun()
```

**Option B: Manual initialization**
Run the init script once after deployment via Streamlit Cloud's terminal or add a setup page.

---

## ⚠️ Important Considerations

### Database Persistence
- **SQLite files are NOT persistent on Streamlit Cloud** by default
- Data will be lost when the app restarts
- **Solutions:**
  1. Use a cloud database (PostgreSQL, MySQL) - **Recommended for production**
  2. Use Streamlit Cloud's persistent storage (if available)
  3. Implement database backup/restore functionality

### Environment Variables
- Never commit API keys or secrets to Git
- Use Streamlit Cloud's Secrets feature
- Update `.gitignore` to exclude sensitive files

### File Paths
- The app uses absolute paths (already fixed in `app/database/config.py`)
- This should work correctly on Streamlit Cloud

### Dependencies
- All required packages are in `requirements.txt`
- Streamlit Cloud will install them automatically

---

## 🔧 Post-Deployment Checklist

- [ ] Verify app loads without errors
- [ ] Test database initialization
- [ ] Test customer/supplier creation
- [ ] Test dashboard functionality
- [ ] Verify business switching works
- [ ] Test AI Advisor (requires API key)
- [ ] Test email functionality (if configured)
- [ ] Monitor for any path-related errors
- [ ] Set up database backup strategy

---

## 📝 Additional Notes

### For Production Use:
1. **Replace SQLite with PostgreSQL:**
   - Update `DATABASE_URL` in secrets
   - Update `app/database/config.py` to use PostgreSQL connection string
   - Test database migrations

2. **Add Error Handling:**
   - Add try-catch blocks for database operations
   - Add user-friendly error messages
   - Log errors for debugging

3. **Performance Optimization:**
   - Add database connection pooling
   - Implement caching for frequently accessed data
   - Optimize queries

4. **Security:**
   - Review and secure API endpoints
   - Implement proper authentication (if needed)
   - Sanitize user inputs

---

## 🆘 Troubleshooting

### App won't start:
- Check that `main file path` is set to `island_harvest_hub/main.py`
- Verify all dependencies in `requirements.txt`
- Check Streamlit Cloud logs for errors

### Database errors:
- Ensure database auto-initialization is working
- Check file permissions
- Verify database path is correct

### Import errors:
- Check Python path configuration
- Verify all modules are in the repository
- Check for missing `__init__.py` files

---

**Ready to deploy!** 🚀


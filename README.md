# Island Harvest Hub AI Assistant

A comprehensive business management system for farm-to-table distribution operations in Jamaica.

## 🚀 Streamlit Cloud Deployment

This application is configured for deployment on Streamlit Cloud.

### Quick Start

1. **Fork or clone this repository**

2. **Deploy to Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub repository
   - Set the main file path: `island_harvest_hub/main.py`
   - Click "Deploy"

3. **Configure Secrets:**
   - In Streamlit Cloud, go to Settings → Secrets
   - Add your environment variables:
     ```toml
     # API Key
     ANTHROPIC_API_KEY = "your_api_key_here"
     
     # Database (optional, defaults to SQLite)
     DATABASE_URL = "sqlite:///island_harvest_hub.db"
     
     # Authentication (required for security)
     [auth]
     username = "admin"
     password_hash = "<generate_with_generate_password_hash.py>"
     ```
   
   **Generate password hash:**
   ```bash
   cd island_harvest_hub
   python generate_password_hash.py
   ```
   
   See `AUTHENTICATION_SETUP.md` for detailed authentication setup instructions.

### Local Development

1. **Install Python 3.11+** from [python.org](https://python.org)

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database:**
   ```bash
   cd island_harvest_hub
   python init_db.py
   ```

4. **Run database migration (if needed):**
   ```bash
   python migrate_add_business_id.py
   ```

5. **Launch the application:**
   ```bash
   streamlit run island_harvest_hub/main.py
   ```

6. **Open your browser** to http://localhost:8501

## 📋 Features

- **Customer Management** - Track hotels, restaurants, and food service customers
- **Supplier Management** - Coordinate with local farmers and producers  
- **Daily Operations** - Manage orders, deliveries, and quality control
- **Financial Management** - Track revenue, expenses, and profitability
- **Communication Hub** - Email templates and messaging coordination
- **Document Center** - Generate invoices, reports, and business documents
- **Strategic Planning** - Set goals and track business growth
- **AI Advisor** - Get business insights and recommendations

## 🏗️ Project Structure

```
island-harvest-enterprise/
├── island_harvest_hub/          # Main application
│   ├── main.py                   # Streamlit app entry point
│   ├── app/                      # Application modules
│   │   ├── models/               # SQLAlchemy models
│   │   ├── services/             # Business logic services
│   │   ├── database/             # Database configuration
│   │   └── config/               # Business profiles
│   ├── pages/                    # Streamlit pages
│   └── requirements.txt          # Python dependencies
├── requirements.txt              # Root requirements (for Streamlit Cloud)
└── README.md                     # This file
```

## ⚙️ System Requirements

- Python 3.11 or later
- 4GB RAM (8GB recommended)
- 2GB free disk space
- Modern web browser (Chrome, Firefox, Edge, Safari)
- Internet connection for email and communication features

## 📚 Documentation

Complete setup and user documentation is available in `island_harvest_hub/docs/setup_guide.md`

## 🔐 Environment Variables

For local development, create a `.env` file:
```
ANTHROPIC_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///island_harvest_hub.db
```

For Streamlit Cloud, add these in the Secrets section of your app settings.

## 📝 License

Proprietary software created for Island Harvest Hub by Manus AI.

---

**Island Harvest Hub AI Assistant**  
*Connecting Jamaica's farmers with hotels and restaurants*  
*Port Antonio, Portland Parish, Jamaica*


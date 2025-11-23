# Island Harvest Hub - Complete Folder Structure

```
island-harvest-enterprise/
│
├── 📁 island_harvest_hub/              # Main application directory
│   │
│   ├── 📄 main.py                      # Main Streamlit application (1,600+ lines)
│   ├── 📄 init_db.py                   # Database initialization script
│   ├── 📄 populate_sample_data.py      # Sample data population script
│   ├── 📄 db_manager.py                 # Database management & backup system
│   ├── 📄 email_notifier.py             # Email notification service
│   ├── 📄 requirements.txt              # Python dependencies
│   ├── 📄 README.md                     # Project documentation
│   ├── 📄 island_harvest_hub.db         # SQLite database file
│   │
│   ├── 📁 app/                          # Application core
│   │   │
│   │   ├── 📁 database/                 # Database configuration
│   │   │   └── 📄 config.py             # SQLAlchemy database config
│   │   │
│   │   ├── 📁 models/                     # Database models (SQLAlchemy)
│   │   │   └── 📄 __init__.py           # All database models defined here
│   │   │       ├── Customer
│   │   │       ├── Order
│   │   │       ├── OrderItem
│   │   │       ├── Farmer (Supplier)
│   │   │       ├── FarmerPayment
│   │   │       ├── DailyLog
│   │   │       ├── Transaction
│   │   │       ├── Invoice
│   │   │       ├── MessageTemplate
│   │   │       ├── Meeting
│   │   │       ├── FollowUpTask
│   │   │       ├── Document
│   │   │       ├── Goal
│   │   │       ├── PerformanceMetric
│   │   │       └── Partnership
│   │   │
│   │   ├── 📁 services/                # Business logic services
│   │   │   ├── 📄 customer_service.py           # Customer management
│   │   │   ├── 📄 supplier_service.py           # Supplier/farmer management
│   │   │   ├── 📄 operations_service.py         # Daily operations
│   │   │   ├── 📄 financial_service.py         # Financial management
│   │   │   ├── 📄 communication_service.py      # Basic communication
│   │   │   ├── 📄 enhanced_communication_service.py  # Advanced communication
│   │   │   ├── 📄 email_service.py              # Email functionality
│   │   │   ├── 📄 whatsapp_service.py           # WhatsApp templates
│   │   │   ├── 📄 document_service.py           # Document management
│   │   │   ├── 📄 document_generation_service.py  # Document creation
│   │   │   └── 📄 strategic_service.py          # Strategic planning
│   │   │
│   │   ├── 📁 static/                   # Static files (CSS, images, etc.)
│   │   ├── 📁 templates/                 # HTML templates (if needed)
│   │   └── 📁 utils/                    # Utility functions
│   │
│   ├── 📁 pages/                        # Additional Streamlit pages
│   │   └── 📄 database_management.py   # Database management interface
│   │
│   ├── 📁 documents/                    # Document storage
│   │   ├── 📁 backups/                  # Document backups
│   │   ├── 📁 contracts/                # Contract documents
│   │   ├── 📁 invoices/                 # Generated invoices
│   │   ├── 📁 reports/                  # Generated reports
│   │   └── 📁 templates/                # Document templates
│   │
│   ├── 📁 docs/                         # Documentation
│   │   ├── 📄 database_schema.md        # Database schema documentation
│   │   ├── 📄 setup_guide.md            # Setup and user guide
│   │   └── 📄 Island_Harvest_Hub_Setup_Guide.pdf  # PDF guide
│   │
│   └── 📁 tests/                        # Test files (to be populated)
│
├── 📁 database_backups/                # Automated database backups
│   └── 📄 backup_daily_YYYYMMDD_HHMMSS.db
│
├── 📁 database_reports/                 # HTML database reports
│   └── 📄 monthly_report_YYYYMM.html
│
├── 📁 database_stats/                   # JSON statistics files
│   └── 📄 stats_YYYYMMDD.json
│
├── 📁 documents/                        # Root documents folder
│
├── 📁 venv/                             # Python virtual environment
│   ├── 📁 Scripts/                      # Windows executables
│   │   ├── python.exe
│   │   ├── pip.exe
│   │   ├── streamlit.exe
│   │   └── ...
│   ├── 📁 Lib/                          # Installed packages
│   └── 📄 pyvenv.cfg                    # Virtual environment config
│
├── 📄 island_harvest_hub.db             # Root database file (duplicate)
│
├── 📄 email_config.json                 # Email configuration (Hostinger)
│
├── 📄 start_island_harvest.bat          # Quick start script
├── 📄 manage_database.bat               # Database maintenance script
├── 📄 setup_db_tasks.bat                # Task scheduler setup
├── 📄 setup.py                          # Installation script
│
├── 📄 db_manager.log                    # Database manager logs
├── 📄 email_notifier.log                # Email notification logs
│
├── 📄 PROJECT_OVERVIEW.md                # Project overview document
├── 📄 FOLDER_STRUCTURE.md               # This file
└── 📄 .gitignore                        # Git ignore rules
```

---

## 📂 Key Directories Explained

### **island_harvest_hub/** - Main Application
- **main.py**: Entry point for the Streamlit application
- **app/**: Core application code organized by function
- **pages/**: Additional Streamlit pages (multi-page app)
- **documents/**: Storage for generated documents
- **docs/**: Project documentation

### **app/** - Application Core
- **database/**: Database connection and configuration
- **models/**: SQLAlchemy database models (data structure)
- **services/**: Business logic layer (11 service classes)
- **static/**: Static assets (CSS, images)
- **templates/**: HTML templates
- **utils/**: Helper functions

### **app/services/** - Business Services
1. **customer_service.py** - Manage hotels/restaurants
2. **supplier_service.py** - Manage farmers/suppliers
3. **operations_service.py** - Daily operations tracking
4. **financial_service.py** - Financial management
5. **communication_service.py** - Basic messaging
6. **enhanced_communication_service.py** - Advanced messaging
7. **email_service.py** - Email functionality
8. **whatsapp_service.py** - WhatsApp templates
9. **document_service.py** - Document management
10. **document_generation_service.py** - Generate PDFs/Excel
11. **strategic_service.py** - Strategic planning

### **Root Level Files**
- **start_island_harvest.bat** - Launch the application
- **manage_database.bat** - Run database maintenance
- **setup_db_tasks.bat** - Set up automated tasks
- **email_config.json** - Email server configuration
- **island_harvest_hub.db** - SQLite database

### **Generated Directories**
- **database_backups/** - Automated backups (daily/weekly/monthly)
- **database_reports/** - HTML reports
- **database_stats/** - JSON statistics
- **venv/** - Python virtual environment (dependencies)

---

## 📊 File Count Summary

### **Python Files**
- Main application: 1 file (main.py)
- Services: 11 files
- Models: 1 file (all models in __init__.py)
- Utilities: 3 files (db_manager, email_notifier, init_db)
- Pages: 1 file (database_management)
- **Total Python files: ~17**

### **Configuration Files**
- requirements.txt
- email_config.json
- setup.py
- .gitignore

### **Documentation**
- README.md
- setup_guide.md
- database_schema.md
- PROJECT_OVERVIEW.md
- FOLDER_STRUCTURE.md

### **Batch Scripts (Windows)**
- start_island_harvest.bat
- manage_database.bat
- setup_db_tasks.bat

### **Database**
- island_harvest_hub.db (main database)
- Backup files in database_backups/

---

## 🔍 Important File Locations

### **To Start the Application:**
```
start_island_harvest.bat
```

### **To Configure Email:**
```
email_config.json
```

### **To Manage Database:**
```
manage_database.bat
or
island_harvest_hub/pages/database_management.py (web interface)
```

### **Main Application Entry:**
```
island_harvest_hub/main.py
```

### **Database File:**
```
island_harvest_hub/island_harvest_hub.db
```

### **Service Layer:**
```
island_harvest_hub/app/services/
```

### **Database Models:**
```
island_harvest_hub/app/models/__init__.py
```

---

## 📝 Notes

- **__pycache__/** directories are Python bytecode cache (auto-generated)
- **venv/** contains all Python packages (can be large)
- **database_backups/** grows over time (automated cleanup)
- **.gitignore** excludes venv, __pycache__, logs, and database files

---

**Last Updated:** June 2025


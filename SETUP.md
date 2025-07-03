# 🚀 Quick Setup Guide

## Prerequisites
- Python 3.11+
- pip (Python package installer)

## Environment Variables
For security, the application's `SECRET_KEY` is loaded from an environment variable.

- **`MARITIME_SECRET_KEY`**: This is a critical security setting for Flask. It's used to sign session cookies and other security-related tokens.
  - **For Production**: You MUST set this to a strong, unique, and random string. Keep it secret!
    You can generate one using Python:
    ```python
    import secrets
    print(secrets.token_hex(32))
    ```
    Then set it as an environment variable in your production environment.
  - **For Development**: If `MARITIME_SECRET_KEY` is not set, the application will automatically generate a temporary secret key each time it starts and print a warning to the console. This is convenient for development but **NOT SUITABLE FOR PRODUCTION**.

## Installation Steps

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python main.py
   ```
   
   Or alternatively:
   ```bash
   python app.py
   ```

3. **Access the Dashboard**
   - Main Wizard: http://localhost:5000
   - Master Dashboard: http://localhost:5000/master
   - Calendar View: http://localhost:5000/calendar
   - Analytics: http://localhost:5000/analytics

## Test the Auto-Fill Feature

1. Go to the main wizard (http://localhost:5000)
2. Upload either:
   - `complete_comprehensive_test_document.txt`
   - `complete_comprehensive_test_document.pdf`
3. Watch as all form fields get automatically populated
4. Navigate through the wizard steps to see data persistence

## File Structure

```
maritime-dashboard-current/
├── src/                    # Backend source code
│   ├── main.py            # Main Flask application
│   ├── models/            # Database models
│   └── routes/            # API endpoints
├── static/                # Frontend files
│   ├── index.html         # Main wizard interface
│   ├── master-dashboard.html
│   ├── calendar.html
│   └── analytics.html
├── database/              # SQLite database directory
├── uploads/               # File upload directory
├── main.py               # Application entry point
├── app.py                # Alternative entry point
├── requirements.txt      # Python dependencies
├── README.md            # Full documentation
└── SETUP.md             # This file
```

## Features Included

✅ 4-Step Wizard with Auto-Fill
✅ Master Dashboard for Multi-Ship Operations
✅ Calendar and Analytics Views
✅ Document Upload and Processing
✅ TICO Transportation Management
✅ Real-Time Berth Status Tracking
✅ Comprehensive Test Documents

## Support

For detailed documentation, see README.md
For issues, check the Flask console output for error messages.

---
**Ready to streamline your maritime operations!** 🚢


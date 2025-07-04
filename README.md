# 🚢 The Stevedores Dashboard

A comprehensive maritime operations management system designed for stevedoring companies to streamline vessel operations, team assignments, and cargo handling processes.

## 🌟 Features

### 📋 4-Step Wizard Interface
- **Vessel Information**: Capture vessel details, port information, and operation dates
- **Cargo Configuration**: Manage automobile counts, heavy equipment, and loading targets
- **Operational Parameters**: Set shift schedules, driver assignments, and TICO transportation
- **Dashboard Generation**: Create real-time monitoring dashboards

### 📄 Smart Document Processing
- **Auto-Fill from Documents**: Upload PDF, CSV, or TXT files to automatically populate forms
- **Intelligent Data Extraction**: Parse maritime documents for vessel and operational data
- **Multi-Format Support**: Handle various document formats seamlessly

### 🎛️ Master Dashboard
- **Multi-Ship Operations**: Monitor multiple vessels simultaneously
- **Real-Time Berth Status**: Track berth availability and assignments
- **Team Deployment**: Manage stevedore team assignments across operations
- **Live KPI Tracking**: Monitor active ships, teams, vehicles, and berth occupancy

### 📅 Calendar & Analytics
- **Operation Scheduling**: Calendar view for past, current, and future operations
- **Performance Analytics**: Track operational efficiency and performance metrics
- **Historical Data**: Access past operation records and trends

### 🚛 TICO Transportation Management
- **Vehicle Fleet Tracking**: Manage vans and station wagons for driver transportation
- **Capacity Planning**: Calculate driver transportation requirements
- **Vehicle ID Management**: Track individual vehicle assignments

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Flask
- Modern web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/colbychapman3/The-Stevedores-Dashboard.git
   cd The-Stevedores-Dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

4. **Access the dashboard**
   - Main Wizard: `http://localhost:5000`
   - Master Dashboard: `http://localhost:5000/master`
   - Calendar View: `http://localhost:5000/calendar`
   - Analytics: `http://localhost:5000/analytics`

## 📁 Project Structure

```
The-Stevedores-Dashboard/
├── src/
│   ├── main.py                 # Main Flask application
│   ├── models/                 # Database models
│   └── routes/                 # API endpoints
│       ├── file_processor.py   # Document processing
│       ├── ships.py           # Ship operations
│       └── user.py            # User management
├── static/
│   ├── index.html             # Main wizard interface
│   ├── master-dashboard.html  # Multi-ship dashboard
│   ├── calendar.html          # Calendar view
│   └── analytics.html         # Analytics dashboard
├── uploads/                   # Document upload directory
├── database/                  # SQLite database
├── requirements.txt           # Python dependencies
├── main.py                   # Application entry point
└── README.md                 # This file
```

## 🔧 Configuration

### Environment Variables
- `PORT`: Server port (default: 5000)
- `SECRET_KEY`: Flask secret key for sessions

### Database
- SQLite database automatically created in `database/app.db`
- No additional database setup required

## 📊 API Endpoints

### File Processing
- `POST /api/upload` - Upload maritime documents
- `POST /api/extract` - Extract data from uploaded documents

### Ship Operations
- `GET /api/ships` - List all ship operations
- `POST /api/ships` - Create new ship operation
- `PUT /api/ships/<id>` - Update ship operation
- `DELETE /api/ships/<id>` - Delete ship operation

### User Management
- `POST /api/users` - Create user
- `GET /api/users` - List users

## 🧪 Testing

### Sample Documents
The repository includes comprehensive test documents:
- `complete_comprehensive_test_document.txt` - Full auto-fill test document
- `complete_comprehensive_test_document.pdf` - PDF version for testing
- `test_maritime_operation_complete.csv` - CSV format example

### Testing Auto-Fill
1. Navigate to the main wizard
2. Upload any of the test documents
3. Watch as all form fields populate automatically
4. Proceed through the wizard steps to see data persistence

## 🎯 Use Cases

### Stevedoring Companies
- Manage multiple vessel operations simultaneously
- Track team assignments and performance
- Monitor cargo handling progress
- Generate operational reports

### Port Authorities
- Oversee berth utilization
- Coordinate vessel scheduling
- Track operational efficiency
- Manage resource allocation

### Maritime Logistics
- Plan cargo operations
- Monitor loading/discharge progress
- Coordinate transportation logistics
- Track operational KPIs

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite
- **Document Processing**: PyPDF2
- **Styling**: Tailwind CSS
- **Charts**: Chart.js
- **Icons**: Font Awesome

## 📈 Features in Detail

### Auto-Fill Functionality
The system intelligently extracts data from maritime documents including:
- Vessel information (name, type, port)
- Team assignments (supervisors, managers)
- Operational parameters (dates, shifts, targets)
- TICO transportation details
- Zone allocations and descriptions

### Real-Time Dashboard
- Live clock and operational status
- Dynamic berth availability
- Team deployment tracking
- Vehicle capacity monitoring
- Progress indicators and KPIs

### Multi-Step Wizard
- Guided data entry process
- Session persistence across steps
- Validation and error handling
- Progress indicators
- Responsive design for mobile/desktop

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, please contact:
- Email: support@stevedores-dashboard.com
- Issues: [GitHub Issues](https://github.com/colbychapman3/The-Stevedores-Dashboard/issues)

## 🙏 Acknowledgments

- Built for maritime industry professionals
- Designed with stevedoring operations in mind
- Optimized for port and terminal operations
- Created to streamline vessel management processes

---

**The Stevedores Dashboard** - Streamlining Maritime Operations, One Vessel at a Time 🚢


## 📱 PWA Features

This Stevedores Dashboard is now a fully functional Progressive Web App (PWA) with:

- **Installable**: Can be installed on mobile devices like a native app
- **Offline Capable**: Works offline with cached content via service worker
- **Responsive**: Optimized for all screen sizes from mobile to desktop
- **Fast Loading**: Cached resources for improved performance

### Installation
1. Visit the deployed application URL
2. On mobile: Tap "Add to Home Screen" when prompted
3. On desktop: Click the install icon in the address bar
4. The app will install and behave like a native application

### Pages Available
- **Dashboard**: Main overview with key metrics
- **Ships**: Fleet management and tracking
- **Containers**: Container inventory and status
- **Crew**: Workforce management and scheduling
- **Analytics**: Detailed performance analytics
- **Calendar**: Schedule and timeline view

All pages are fully responsive and work offline once cached.
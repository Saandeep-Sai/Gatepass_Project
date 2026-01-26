# QR Code Gate Pass Management System

A comprehensive web-based gate pass management system for educational institutions built with Flask and Firebase. This system enables faculty members to request gate passes, HODs to approve/deny requests, and security personnel to validate QR codes for campus exit.

## 🚀 Features

### Faculty Dashboard
- **Request Gate Pass**: Submit leave requests with detailed reasons
- **Real-time Status Tracking**: View pending, approved, and denied requests
- **QR Code Generation**: Automatic QR code creation upon HOD approval
- **Time Tracking**: View when QR was generated, scanned, and total duration
- **Request History**: Complete history of all requests with timestamps
- **Statistics & Analytics**: Visual representation of request trends

### HOD Dashboard
- **Request Management**: Approve or deny faculty leave requests
- **Priority-based Sorting**: High-priority requests highlighted
- **Real-time Updates**: Auto-refresh every 5 seconds for new requests
- **Historical Data**: View all approved and denied requests
- **Time Tracking**: Monitor QR generation times and checkout durations
- **Faculty Management**: View complete faculty list

### Security Dashboard
- **QR Code Validation**: Scan and verify gate pass QR codes
- **Multi-step Verification**: Validates approval status and usage
- **Checkout Recording**: Automatic timestamp and duration calculation
- **Request Details**: View complete information about the gate pass holder

## 🛠️ Technologies Used

- **Backend**: Flask 2.3.0 (Python Web Framework)
- **Database**: Firebase Firestore (NoSQL Cloud Database)
- **QR Code Generation**: qrcode[pil] 7.3
- **QR Code Scanning**: pyzbar 0.1.9
- **Real-time Communication**: Flask-SocketIO 5.3.6
- **Email Notifications**: Flask-Mail 0.9.1
- **Session Management**: Flask-Session 0.5.0
- **Deployment**: Gunicorn 21.2.0 (Production Server)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla), Chart.js

## 📋 Prerequisites

- Python 3.11 or higher
- Firebase account with Firestore enabled
- Gmail account for email notifications (optional)

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd QR-CODE-GATE-PASS-MANAGEMENT-SYSTEM
```

### 2. Create Virtual Environment
```powershell
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Firebase Configuration

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Firestore Database
3. Generate a service account key:
   - Go to Project Settings → Service Accounts
   - Click "Generate New Private Key"
4. Save the downloaded JSON file as `firebase_config.json` in the project root

### 5. Environment Variables

Create a `.env` file or set environment variables:

```bash
SECRET_KEY=your_secret_key_here
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

**Note**: For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

## 🚀 Running the Application

### Development Mode
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Production Mode
```bash
gunicorn app:app
```

## 📁 Project Structure

```
QR-CODE-GATE-PASS-MANAGEMENT-SYSTEM/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── firebase_config.json        # Firebase credentials (gitignored)
├── .env                        # Environment variables (gitignored)
├── templates/
│   ├── login.html             # Login page
│   ├── hod.html               # HOD dashboard
│   ├── faculty_dashboard.html # Faculty dashboard
│   ├── faculty.html           # Faculty alternative view
│   └── security.html          # Security dashboard
├── photos/                     # User profile photos
└── flask_session/             # Session data
```

## 🔐 User Roles & Access

### Faculty
- **Login**: Use faculty credentials
- **Capabilities**: 
  - Submit gate pass requests
  - View QR codes for approved requests
  - Track request status and history

### HOD (Head of Department)
- **Login**: Use HOD credentials
- **Capabilities**:
  - View all pending faculty requests
  - Approve/deny requests
  - View request history
  - Manage faculty list

### Security
- **Login**: Use security credentials
- **Capabilities**:
  - Validate QR codes
  - Record checkout times
  - View gate pass details

## 🗄️ Database Structure

### Collections

#### `requests`
- `student_id`: Faculty employee ID
- `name`: Faculty name
- `reason`: Leave reason
- `status`: 'Pending', 'Approved', or 'Denied'
- `datetime`: Request submission date
- `priority`: 'high', 'medium', or 'low'
- `generated_at`: QR generation timestamp (ISO format)
- `scanned_at`: QR scan timestamp (ISO format)
- `duration_seconds`: Time between approval and scan
- `checkedout`: Boolean flag
- `key`: 6-digit verification key
- `qr_base64`: Base64 encoded QR code image

#### `facultydata`
User authentication data for faculty members

#### `hoddata`
User authentication data for HODs

#### `securitydata`
User authentication data for security personnel

## ⏱️ Time Tracking Features

- **QR Generated At**: Timestamp when HOD approves the request
- **Scanned At**: Timestamp when security validates the QR code
- **Duration**: Automatic calculation of time spent outside campus
- **Format**: DD-MM-YYYY HH:MM:SS for display, ISO format for storage

## 🔄 Real-time Updates

- HOD dashboard auto-refreshes every 5 seconds
- Dynamic table updates without page reload
- Live statistics updates via API endpoint

## 📧 Email Notifications

Automatic email notifications sent when:
- Request is approved
- Request is denied
- QR code is generated

## 🎨 UI Features

- Responsive design for mobile and desktop
- Color-coded priority levels (High: Red, Medium: Orange, Low: Green)
- Status indicators (Approved: Green, Pending: Orange, Denied: Red)
- Interactive charts for statistics
- QR code display with download option

## 🔒 Security Features

- Session-based authentication
- Role-based access control
- QR code expiration (used status)
- Multi-step verification process
- Cache control headers to prevent stale data

## 🐛 Troubleshooting

### Firebase Connection Issues
- Verify `firebase_config.json` is in the project root
- Check Firebase project permissions
- Ensure Firestore is enabled in Firebase Console

### Email Not Sending
- Verify Gmail App Password is correct
- Check if "Less secure app access" is enabled (if applicable)
- Verify SMTP settings in `app.py`

### QR Code Not Displaying
- Check if `qrcode[pil]` is installed correctly
- Verify the request has been approved
- Clear browser cache

## 📝 Default Login Credentials

**Note**: Update these in your Firebase collections before deployment.

You need to add users to the respective collections (`facultydata`, `hoddata`, `securitydata`) in Firestore.

## 🚀 Deployment

The application is ready for deployment on platforms like:
- Render.com
- Heroku
- Google Cloud Platform
- AWS

Ensure to:
1. Set environment variables on the platform
2. Upload `firebase_config.json` securely
3. Use gunicorn as the production server

## 📄 License

This project is created for educational purposes.

## 👥 Contributors

CMR Institute of Technology - Gate Pass Management System

## 📞 Support

For issues or questions, please create an issue in the repository or contact the development team.

---

**Version**: 2.0  
**Last Updated**: January 2026

# Deployment Instructions for Render

## Prerequisites
1. Firebase project with Firestore enabled
2. Firebase service account JSON file
3. GitHub repository

## Steps to Deploy

### 1. Prepare Firebase Configuration
- Download your Firebase service account JSON file
- In Render dashboard, add it as a secret file named `firebase_config.json`

### 2. Environment Variables (Set in Render Dashboard)
```
SECRET_KEY=your-random-secret-key-here
PYTHON_VERSION=3.9.0
```

### 3. Deploy on Render
1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Select your repository
4. Render will auto-detect the configuration from `render.yaml`
5. Add the `firebase_config.json` as a secret file
6. Deploy!

### 4. Post-Deployment
- Create HOD, Faculty, and Security accounts in Firebase
- Test login functionality
- Verify Firebase connection

## Important Notes
- The app uses Flask-SocketIO for real-time updates
- Sessions are stored in filesystem (consider Redis for production)
- Firebase credentials must be kept secure
- Change SECRET_KEY in production

## Collections Required in Firestore
- `hoddata` - HOD login credentials
- `facultydata` - Faculty login credentials  
- `securitydata` - Security login credentials
- `faculty` - Faculty profile data
- `requests` - Leave/gate pass requests
- `visitors` - Visitor logs

## Default Login Types
- Faculty
- HOD
- Security

Student functionality has been removed.

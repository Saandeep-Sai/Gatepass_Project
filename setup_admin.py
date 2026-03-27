"""
One-time script to seed the default admin account into Firestore.
Run: python setup_admin.py
"""
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('firebase_config.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def seed_admin():
    # Check if admin already exists
    existing = next(db.collection('admindata').where('username', '==', 'admin').limit(1).stream(), None)
    if existing:
        print("Admin account already exists. Skipping.")
        return

    db.collection('admindata').add({
        'username': 'admin',
        'password': 'admin123',
        'role': 'admin'
    })
    print("Default admin account created successfully!")
    print("  Username: admin")
    print("  Password: admin123")

if __name__ == '__main__':
    seed_admin()

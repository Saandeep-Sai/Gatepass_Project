import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

try:
    # Initialize Firebase
    cred = credentials.Certificate('firebase_config.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✓ Firebase connected successfully")
    
    # Test write operation
    test_data = {
        'student_id': 'TEST_FACULTY',
        'name': 'Test Faculty',
        'reason': 'Test request',
        'status': 'Pending',
        'datetime': datetime.now().date().strftime('%d-%m-%Y'),
        'priority': 'low',
        'faculty': 'hod',
        'checkedout': False,
        'checkouttime': None,
        'type': 'faculty'
    }
    
    doc_ref = db.collection('requests').add(test_data)
    print(f"✓ Test request saved successfully with ID: {doc_ref[1].id}")
    
    # Clean up test data
    db.collection('requests').document(doc_ref[1].id).delete()
    print("✓ Test data cleaned up")
    
except Exception as e:
    print(f"✗ Error: {e}")

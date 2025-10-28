import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate('firebase_config.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def update_all_students():
    """Update all students to have faculty1 as their mentor"""
    
    # Get all students from studentdata
    student_logins = db.collection('studentdata').stream()
    
    for student_doc in student_logins:
        student_data = student_doc.to_dict()
        username = student_data.get('username')
        
        if username:
            # Check if student profile exists
            existing_profile = next(db.collection('students').where('username', '==', username).limit(1).stream(), None)
            
            if existing_profile:
                # Update existing profile
                db.collection('students').document(existing_profile.id).update({
                    'faculty': 'faculty1',
                    'name': existing_profile.to_dict().get('name', username)
                })
                print(f"Updated student profile: {username}")
            else:
                # Create new profile
                db.collection('students').add({
                    'username': username,
                    'name': username,
                    'faculty': 'faculty1'
                })
                print(f"Created student profile: {username}")
    
    # Update all existing requests to have faculty1
    requests = db.collection('requests').stream()
    count = 0
    for req_doc in requests:
        db.collection('requests').document(req_doc.id).update({'faculty': 'faculty1'})
        count += 1
    
    print(f"\nUpdated {count} requests to faculty1")
    print("\nAll students now assigned to Dr. S. Rao Chintalapudi (faculty1)")

if __name__ == '__main__':
    update_all_students()

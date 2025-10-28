import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate('firebase_config.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Sample data setup
def setup_sample_data():
    # Add Dr. S. Rao Chintalapudi as the single faculty
    faculty_username = "Dr. S. Rao Chintalapudi"
    faculty_data = {
        'username': faculty_username,
        'password': '123456789',
        'photo': 'Dr._S._Rao_Chintalapudi.jpg',
        'name': 'Dr. S. Rao Chintalapudi'
    }
    
    # Check if faculty exists
    existing_faculty = next(db.collection('facultydata').where('username', '==', faculty_username).limit(1).stream(), None)
    if not existing_faculty:
        db.collection('facultydata').add(faculty_data)
        print(f"Added faculty: Dr. S. Rao Chintalapudi (username: {faculty_username})")
    else:
        db.collection('facultydata').document(existing_faculty.id).update({'name': 'Dr. S. Rao Chintalapudi', 'photo': 'Dr._S._Rao_Chintalapudi.jpg'})
        print(f"Updated faculty: Dr. S. Rao Chintalapudi (username: {faculty_username})")
    
    # Add a sample student with faculty assigned
    student_username = "20EG112305"
    student_name = "Test Student"
    
    # Add to studentdata (login credentials)
    student_login = {
        'username': student_username,
        'password': 'password',
        'photo': f'{student_username}.jpg'
    }
    
    existing_student_login = next(db.collection('studentdata').where('username', '==', student_username).limit(1).stream(), None)
    if not existing_student_login:
        db.collection('studentdata').add(student_login)
        print(f"Added student login: {student_username}")
    else:
        print(f"Student login {student_username} already exists")
    
    # Add to students (profile with faculty)
    student_profile = {
        'username': student_username,
        'name': student_name,
        'faculty': faculty_username
    }
    
    existing_student_profile = next(db.collection('students').where('username', '==', student_username).limit(1).stream(), None)
    if not existing_student_profile:
        db.collection('students').add(student_profile)
        print(f"Added student profile: {student_username} with faculty: {faculty_username}")
    else:
        # Update existing profile to ensure faculty is set
        db.collection('students').document(existing_student_profile.id).update({'faculty': faculty_username, 'name': student_name})
        print(f"Updated student profile: {student_username}")

if __name__ == '__main__':
    setup_sample_data()
    print("\nSetup complete!")
    print("\nYou can now login with:")
    print("Student: 20EG112305 / password")
    print("Faculty: faculty1 / password (Dr. S. Rao Chintalapudi)")

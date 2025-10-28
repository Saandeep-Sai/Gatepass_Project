import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate('firebase_config.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

faculty_data = [
    {"emp_id": "2204", "name": "Dr D T V Dharmajee Rao"},
    {"emp_id": "2161", "name": "Dr. S Rao Chintalapudi"},
    {"emp_id": "2151", "name": "Dr. G Vinoda Reddy"},
    {"emp_id": "2110", "name": "Dr. K Mahesh"},
    {"emp_id": "2131", "name": "Dr.Md.Shareef"},
    {"emp_id": "2160", "name": "Dr.V.Malsoru"},
    {"emp_id": "2130", "name": "Shaik Sharif"},
    {"emp_id": "2139", "name": "G.Parvathi Devi"},
    {"emp_id": "8150", "name": "V.Srinu"},
    {"emp_id": "2159", "name": "M.Ravindran"},
    {"emp_id": "2168", "name": "V.RavinderNaik"},
    {"emp_id": "2210", "name": "S.Rama Chandrareddy"},
    {"emp_id": "2221", "name": "Bushra Tarannum"},
    {"emp_id": "2238", "name": "U.Saritha"},
    {"emp_id": "2195", "name": "Swaroopa Rani B"},
    {"emp_id": "2199", "name": "B. Prashanth"},
    {"emp_id": "2243", "name": "Ramesh Azmeera"},
    {"emp_id": "2267", "name": "R.Lavanya"},
    {"emp_id": "2216", "name": "G.Aravind"},
    {"emp_id": "2231", "name": "Mrs.M.Lalitha"},
    {"emp_id": "2295", "name": "N.Sandeep Kumar"},
    {"emp_id": "2306", "name": "B.Ravindranaik"},
    {"emp_id": "2288", "name": "K.Bhargava Trivenei nandana"},
    {"emp_id": "2250", "name": "S.Kiran"},
    {"emp_id": "2252", "name": "G.Pavan"},
    {"emp_id": "2251", "name": "K.Madhu"},
    {"emp_id": "2255", "name": "K.Nagamani"},
    {"emp_id": "2264", "name": "Swathi Rudra"},
    {"emp_id": "2269", "name": "P.Rashmitha"},
    {"emp_id": "2148", "name": "Mudadla Balaji"},
    {"emp_id": "2314", "name": "I Kranthi Kumar"},
    {"emp_id": "2281", "name": "G.Sravan Rao"},
    {"emp_id": "2283", "name": "P.Vishnu"},
    {"emp_id": "2240", "name": "B Aditya"},
    {"emp_id": "2316", "name": "G.Mahabub Subhani"},
    {"emp_id": "2381", "name": "A Prashanthi"}
]

def setup_faculty():
    # Add faculty members
    for faculty in faculty_data:
        existing = next(db.collection('faculty').where('emp_id', '==', faculty['emp_id']).limit(1).stream(), None)
        if not existing:
            db.collection('faculty').add(faculty)
            print(f"Added faculty: {faculty['name']} ({faculty['emp_id']})")
        else:
            print(f"Faculty already exists: {faculty['name']}")
    
    # Add faculty login credentials (emp_id as username, password: password)
    for faculty in faculty_data:
        existing = next(db.collection('facultydata').where('username', '==', faculty['emp_id']).limit(1).stream(), None)
        if not existing:
            db.collection('facultydata').add({
                'username': faculty['emp_id'],
                'password': 'password',
                'photo': f"{faculty['emp_id']}.jpg"
            })
            print(f"Added login for: {faculty['emp_id']}")
    
    # Add HOD login (Dr. S Rao Chintalapudi)
    hod_username = "hod"
    existing_hod = next(db.collection('hoddata').where('username', '==', hod_username).limit(1).stream(), None)
    if not existing_hod:
        db.collection('hoddata').add({
            'username': hod_username,
            'password': 'password',
            'photo': 'Dr._S._Rao_Chintalapudi.jpg',
            'name': 'Dr. S Rao Chintalapudi'
        })
        print("Added HOD login")
    else:
        print("HOD login already exists")

if __name__ == '__main__':
    setup_faculty()
    print("\nSetup complete!")
    print("\nLogin credentials:")
    print("HOD: username=hod, password=password")
    print("Faculty: username=<emp_id>, password=password")
    print("Example: username=2161, password=password")

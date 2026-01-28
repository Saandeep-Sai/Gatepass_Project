from flask import *
import firebase_admin
from firebase_admin import credentials, firestore
from flask_session import Session
import random
import qrcode
from io import BytesIO
from datetime import datetime
from pyzbar import *
from flask_socketio import SocketIO
import base64
from werkzeug.utils import secure_filename
import os
from flask_mail import Mail, Message
import time


app = Flask(__name__)
socketio = SocketIO(app)
UPLOAD_FOLDER = 'photos'
ALLOWED_EXTENSIONS = {'jpg'}

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key_change_in_production')  
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

cred = credentials.Certificate('firebase_config.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Spacy removed for deployment optimization

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'poppingaming1@gmail.com'
app.config['MAIL_PASSWORD'] = 'atjj cynj vkwt ljkn'

mail = Mail(app)

@app.after_request
def add_cache_control(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring and deployment platforms"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'CMR Gate Pass Management System'
    }), 200

def prioritize_text(text):
    text_lower = text.lower()
    
    priority_keywords = {
        "urgent": 3,
        "health": 2,
        "emergency": 3,
        "family emergency": 2,
        "personal reasons": 1,
        "vacation": 1,
        "wedding": 1,
        "birth of a child": 1,
        "fever": 2,
        "headache": 2,
        "stomach pain": 2,
        "educational purposes": 1,
        "unplanned event": 1,
        "death": 3,
        "injury": 3,
        "exam": 3,
        "education": 3,    
    }

    priority_labels = {
    3: "high",
    2: "medium",
    1: "low",
    }

    priority = 1  

    for keyword, weight in priority_keywords.items():
        if keyword in text_lower:
            priority = max(priority, weight)

    return priority_labels[priority]


@app.route('/', methods=['GET', 'POST'])
def login():
    if session.get("login_type"):
        if (session["login_type"] == 'wrong'):
            return redirect('/wrong')
        elif (session["login_type"] == "faculty"):
            return redirect(url_for('faculty'))
        elif (session["login_type"] == "faculty"):
            return redirect(url_for('faculty'))
        elif (session["login_type"] == "hod"):
            return redirect(url_for('hod'))
        elif (session["login_type"] == "security"):
            return redirect(url_for('security'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        login_type = request.form['login_type']
        session["username"] = request.form['username']
        session["login_type"] = request.form['login_type']

        user_data = None
        # Only faculty, hod and security logins are allowed now
        if login_type == 'faculty':
            users = db.collection('facultydata').where('username', '==', username).where('password', '==', password).limit(1).stream()
            user_data = next(users, None)
            if user_data:
                user_doc = db.collection('faculty').where('emp_id', '==', username).limit(1).stream()
                user = next(user_doc, None)
                if user:
                    session['name'] = user.to_dict().get('name', '')
        elif login_type == 'hod':
            users = db.collection('hoddata').where('username', '==', username).where('password', '==', password).limit(1).stream()
            user_data = next(users, None)
        elif login_type == 'security':
            users = db.collection('securitydata').where('username', '==', username).where('password', '==', password).limit(1).stream()
            user_data = next(users, None)
        else:
            # student or other roles are no longer supported
            user_data = None

        if user_data:
            session['login_type'] = login_type
            if login_type == 'faculty':
                return redirect(url_for('faculty'))
            elif login_type == 'hod':
                return redirect(url_for('hod'))
            elif login_type == 'security':
                return redirect(url_for('security'))
        else:
            session["username"] = None
            session["name"] = None
            session["login_type"] = 'wrong'
            return redirect("/")

    return render_template('index.html')

@app.route("/logout")
def logout():
    session["login_type"] = None
    session["username"] = None
    session["name"] = None
    
    return redirect("/")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/faculty-list')
def get_faculty_list():
    faculty_docs = db.collection('facultydata').stream()
    faculty_list = [{'username': doc.to_dict().get('username')} for doc in faculty_docs]
    return jsonify(faculty_list)

@app.route('/api/faculty/requests')
def get_faculty_requests():
    if 'login_type' not in session or session['login_type'] != 'hod':
        return jsonify({'error': 'Unauthorized'}), 401
    
    current_date = datetime.now().date().strftime('%d-%m-%Y')
    
    all_requests = db.collection('requests').where('type', '==', 'faculty').stream()
    all_requests_list = []
    
    for doc in all_requests:
        request_data = {'_id': doc.id, **doc.to_dict()}
        
        # Format check-in time (generated_at) and checkout time (scanned_at) for display
        if request_data.get('generated_at'):
            try:
                gen_dt = datetime.fromisoformat(request_data['generated_at'])
                request_data['check_in_time'] = gen_dt.strftime('%d-%m-%Y %H:%M:%S')
            except:
                request_data['check_in_time'] = 'N/A'
        else:
            request_data['check_in_time'] = 'N/A'
        
        if request_data.get('scanned_at'):
            try:
                scan_dt = datetime.fromisoformat(request_data['scanned_at'])
                request_data['checkout_time_display'] = scan_dt.strftime('%d-%m-%Y %H:%M:%S')
            except:
                request_data['checkout_time_display'] = 'N/A'
        else:
            request_data['checkout_time_display'] = 'Not Scanned'
        
        # Format duration if available
        if request_data.get('duration_seconds'):
            duration_sec = int(request_data['duration_seconds'])
            hours = duration_sec // 3600
            minutes = (duration_sec % 3600) // 60
            seconds = duration_sec % 60
            request_data['duration_display'] = f"{hours}h {minutes}m {seconds}s"
        else:
            request_data['duration_display'] = 'N/A'
        
        all_requests_list.append(request_data)
    
    faculty_pending = [r for r in all_requests_list if r.get('status') == 'Pending']
    faculty_approved = [r for r in all_requests_list if r.get('status') == 'Approved' and r.get('datetime') == current_date]
    faculty_denied = [r for r in all_requests_list if r.get('status') == 'Denied' and r.get('datetime') == current_date]
    
    return jsonify({
        'faculty_pending': faculty_pending,
        'faculty_approved': faculty_approved,
        'faculty_denied': faculty_denied
    })

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        login_type = request.form['login_type']
        photo = request.files['photo']

        if photo.filename == '':
            flash('No file selected. Please upload a photo.', 'error')
            return redirect(url_for('register'))
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            filename = secure_filename(username) + os.path.splitext(filename)[1]
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            flash('Unsupported file format. Please upload a JPG image.', 'error')
            return redirect(url_for('register'))

        existing_user = next(db.collection(f'{login_type}data').where('username', '==', username).limit(1).stream(), None)
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'error')
            return redirect(url_for('register'))

        if login_type == 'faculty':
            db.collection('facultydata').add({'username': username, 'password': password, 'photo': filename})
        elif login_type == 'security':
            db.collection('securitydata').add({'username': username, 'password': password, 'photo': filename})
        else:
            flash('Invalid registration type.', 'error')
            return redirect(url_for('register'))

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Student functionality removed per client request. Students no longer submit or view requests.

@app.route('/photos/<path:filename>')
def photos(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_from_directory('photos', filename)
    else:
        abort(404)

@app.route('/hod', methods=['GET', 'POST'])
def hod():
    if 'login_type' not in session or session['login_type'] != 'hod':
        return redirect(url_for('login'))

    if request.method == 'POST':
        request_id = request.form['request_id']
        action = request.form['action']

        if action == 'allow':
            random_key = str(random.randint(100000, 999999))
            generated_at = datetime.now().isoformat()
            db.collection('requests').document(request_id).update({'status': 'Approved', 'key': random_key, 'generated_at': generated_at})
        elif action == 'deny':
            db.collection('requests').document(request_id).update({'status': 'Denied', 'key': None})
        
        return redirect(url_for('hod'))

    current_date = datetime.now().date().strftime('%d-%m-%Y')
    
    # Fetch ALL faculty requests (not filtered by date for history)
    all_requests = db.collection('requests').where('type', '==', 'faculty').stream()
    all_requests_list = []
    
    for doc in all_requests:
        request_data = {'_id': doc.id, **doc.to_dict()}
        
        # Format check-in time (generated_at) and checkout time (scanned_at) for display
        if request_data.get('generated_at'):
            try:
                gen_dt = datetime.fromisoformat(request_data['generated_at'])
                request_data['check_in_time'] = gen_dt.strftime('%d-%m-%Y %H:%M:%S')
            except:
                request_data['check_in_time'] = 'N/A'
        else:
            request_data['check_in_time'] = 'N/A'
        
        if request_data.get('scanned_at'):
            try:
                scan_dt = datetime.fromisoformat(request_data['scanned_at'])
                request_data['checkout_time_display'] = scan_dt.strftime('%d-%m-%Y %H:%M:%S')
            except:
                request_data['checkout_time_display'] = 'N/A'
        else:
            request_data['checkout_time_display'] = 'Not Scanned'
        
        # Format duration if available
        if request_data.get('duration_seconds'):
            duration_sec = int(request_data['duration_seconds'])
            hours = duration_sec // 3600
            minutes = (duration_sec % 3600) // 60
            seconds = duration_sec % 60
            request_data['duration_display'] = f"{hours}h {minutes}m {seconds}s"
        else:
            request_data['duration_display'] = 'N/A'
        
        all_requests_list.append(request_data)
    
    # Pending requests (all dates)
    faculty_pending = [r for r in all_requests_list if r.get('status') == 'Pending']
    
    # Approved requests (today only for quick view)
    faculty_approved_today = [r for r in all_requests_list if r.get('status') == 'Approved' and r.get('datetime') == current_date]
    
    # All approved requests (history - all dates)
    faculty_approved_all = [r for r in all_requests_list if r.get('status') == 'Approved']
    
    # Denied requests (today only)
    faculty_denied_today = [r for r in all_requests_list if r.get('status') == 'Denied' and r.get('datetime') == current_date]
    
    # All denied requests (history - all dates)
    faculty_denied_all = [r for r in all_requests_list if r.get('status') == 'Denied']
    
    total_faculty_docs = db.collection('faculty').stream()
    total_faculty = [doc.to_dict() for doc in total_faculty_docs]

    return render_template('hod.html', 
                         faculty_pending=faculty_pending,
                         faculty_approved=faculty_approved_today,
                         faculty_approved_all=faculty_approved_all,
                         faculty_denied=faculty_denied_today,
                         faculty_denied_all=faculty_denied_all,
                         total_faculty=total_faculty)

@app.route('/faculty', methods=['GET', 'POST'])
def faculty():
    if 'login_type' not in session or session['login_type'] != 'faculty':
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            faculty_id = session['username']
            name = session.get('name', faculty_id)
            reason = request.form.get('reason', '')
            
            if not reason:
                flash('Please provide a reason for your request.', 'error')
                return redirect(url_for('faculty'))
            
            priority = prioritize_text(reason)
            current_date = datetime.now().date().strftime('%d-%m-%Y')
            
            request_data = {
                'student_id': faculty_id,
                'name': name,
                'reason': reason,
                'status': 'Pending',
                'datetime': current_date,
                'priority': priority,
                'faculty': 'hod',
                'checkedout': False,
                'checkouttime': None,
                'type': 'faculty'
            }
            
            db.collection('requests').add(request_data)
            print(f"Faculty request saved: {request_data}")
            flash('Request submitted successfully!', 'success')
        except Exception as e:
            print(f"Error saving faculty request: {e}")
            flash('Error submitting request. Please try again.', 'error')
        
        return redirect(url_for('faculty'))

    faculty_id = session['username']
    requests_docs = db.collection('requests').where('student_id', '==', faculty_id).stream()
    
    requests = []
    for doc in requests_docs:
        request_data = {'id': doc.id, **doc.to_dict()}
        
        # Format check-in time (generated_at) and checkout time (scanned_at) for display
        if request_data.get('generated_at'):
            try:
                gen_dt = datetime.fromisoformat(request_data['generated_at'])
                request_data['check_in_time'] = gen_dt.strftime('%d-%m-%Y %H:%M:%S')
            except:
                request_data['check_in_time'] = 'N/A'
        else:
            request_data['check_in_time'] = 'Not Approved Yet'
        
        if request_data.get('scanned_at'):
            try:
                scan_dt = datetime.fromisoformat(request_data['scanned_at'])
                request_data['checkout_time_display'] = scan_dt.strftime('%d-%m-%Y %H:%M:%S')
            except:
                request_data['checkout_time_display'] = 'N/A'
        else:
            request_data['checkout_time_display'] = 'Not Scanned'
        
        # Format duration if available
        if request_data.get('duration_seconds'):
            duration_sec = int(request_data['duration_seconds'])
            hours = duration_sec // 3600
            minutes = (duration_sec % 3600) // 60
            seconds = duration_sec % 60
            request_data['duration_display'] = f"{hours}h {minutes}m {seconds}s"
        else:
            request_data['duration_display'] = 'N/A'
        
        requests.append(request_data)
    
    # Show all approved requests (not just today's) in Active QR Codes section
    approved_requests = [req for req in requests if req.get('status') == 'Approved']

    return render_template('faculty_dashboard.html', requests=requests, approved_requests=approved_requests)

@app.route('/security', methods=['GET', 'POST'])
def security():
    if 'login_type' not in session or session['login_type'] != 'security':
        return redirect(url_for('login'))

    # Get today's checkout logs
    current_date = datetime.now().date().strftime('%d-%m-%Y')
    checkout_logs_docs = db.collection('requests').where('checkedout', '==', True).where('datetime', '==', current_date).stream()
    checkout_logs = [doc.to_dict() for doc in checkout_logs_docs]

    return render_template('security_dashboard.html', checkout_logs=checkout_logs)

@app.route('/security/validate-qr/<key>', methods=['POST'])
def validate_qr(key):
    current_date = datetime.now().date().strftime('%d-%m-%Y')
    current_time = datetime.now()

    request_doc = next(db.collection('requests').where('key', '==', key).limit(1).stream(), None)

    if not request_doc:
        return jsonify({'success': False, 'message': 'Invalid QR code'})

    request_data = request_doc.to_dict()

    if request_data.get('status') != 'Approved':
        return jsonify({'success': False, 'message': 'Pass not approved'})

    if request_data.get('checkedout') == True:
        return jsonify({'success': False, 'message': 'QR code already used'})

    if request_data.get('datetime') != current_date:
        return jsonify({'success': False, 'message': 'QR code expired'})

    # Compute scanned_at and duration (seconds) relative to generated_at
    generated_at_str = request_data.get('generated_at')
    scanned_at = current_time.isoformat()
    duration_seconds = None
    if generated_at_str:
        try:
            gen_dt = datetime.fromisoformat(generated_at_str)
            duration_seconds = (current_time - gen_dt).total_seconds()
        except Exception:
            duration_seconds = None

    # Mark as checked out and save scanned time and duration
    update_fields = {
        'checkedout': True,
        'checkouttime': current_time.strftime('%H:%M:%S'),
        'scanned_at': scanned_at
    }
    if duration_seconds is not None:
        update_fields['duration_seconds'] = duration_seconds

    db.collection('requests').document(request_doc.id).update(update_fields)

    return jsonify({
        'success': True,
        'name': request_data.get('name'),
        'student_id': request_data.get('student_id'),
        'reason': request_data.get('reason'),
        'scanned_at': scanned_at,
        'duration_seconds': duration_seconds
    })

@app.route('/security/visitors_log')
def visitors_log():
    if 'login_type' not in session or session['login_type'] not in ['faculty', 'security']:
        return redirect(url_for('login'))
    visitors = db.collection('visitors').stream()
    visitors_list = [{'id': doc.id, **doc.to_dict()} for doc in visitors]

    return render_template('visitors_log.html', visitors=visitors_list)

@app.route('/security/checkout/<visitor_id>', methods=['POST'])
def checkout_visitor(visitor_id):
    checkout_time = datetime.now()
    db.collection('visitors').document(visitor_id).update({'checkout': True, 'checkout_time': checkout_time})
    return redirect(url_for('visitors_log'))

@app.route('/view_requests', methods=['GET', 'POST'])
def view_requests():
    # Student request view removed. This endpoint is deprecated.
    return redirect(url_for('hod'))

@app.route('/generate_qr/<key>')
def generate_qr(key):
    # Validate that the key belongs to an approved request in Firestore
    request_ref = db.collection('requests').where('key', '==', key).where('status', '==', 'Approved').limit(1)
    docs = list(request_ref.stream())
    if not docs:
        return "Invalid or unauthorized QR code generation. Request must be approved first.", 403

    qr_url = f"https://augatepass.onrender.com/verifyqr/{key}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    img_io = BytesIO()
    img.save(img_io)
    img_io.seek(0)
    # Convert image to base64
    qr_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

    # Save QR code base64 to Firestore under the request document
    doc_id = docs[0].id
    db.collection('requests').document(doc_id).update({'qr_base64': qr_base64})

    return send_file(img_io, mimetype='image/png')

@app.route('/verifyqr/<key>')
def verify_qr(key):
    current_date = datetime.now().date().strftime('%d-%m-%Y')
    request_doc = next(db.collection('requests').where('key', '==', key).limit(1).stream(), None)

    if not request_doc:
        return render_template('verify_qr_error.html', message='Invalid QR code. Request not found.')

    request_data = request_doc.to_dict()

    if request_data.get('status') != 'Approved':
        return render_template('verify_qr_error.html', message='QR code not valid. Request has not been approved yet.')

    checkedout_value = request_data.get('checkedout')
    if checkedout_value == True or checkedout_value == 'True':
        return render_template('verify_qr_error.html', message='QR code already used. Student has already checked out.')

    if request_data.get('datetime') != current_date:
        return render_template('verify_qr_error.html', message='QR code expired. Valid only for the date: ' + request_data.get('datetime', 'N/A'))

    # Show generated/scanned timestamps and duration if present
    generated_at = request_data.get('generated_at')
    scanned_at = request_data.get('scanned_at')
    duration_seconds = request_data.get('duration_seconds')

    return render_template('verify_qr.html', key=request_data['key'], student_id=request_data['student_id'], name=request_data['name'], reason=request_data['reason'], datetime=request_data['datetime'], generated_at=generated_at, scanned_at=scanned_at, duration_seconds=duration_seconds)
    
@app.route('/change', methods=['GET', 'POST'])
def change():
    if 'login_type' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = session['username']
        current_password = request.form['current_password']
        new_password = request.form['new_password']

        user = None
        if session["login_type"] == 'security':
            user = next(db.collection('securitydata').where('username', '==', username).where('password', '==', current_password).limit(1).stream(), None)
        elif session["login_type"] == 'faculty':
            user = next(db.collection('facultydata').where('username', '==', username).where('password', '==', current_password).limit(1).stream(), None)
        else:
            return "Invalid login type."

        if user:
            db.collection(f"{session['login_type']}data").document(user.id).update({'password': new_password})
            return redirect("/logout")
        else:
            return "Incorrect username or password. Please try again."
    return render_template('change.html')

@app.route('/checkout/<key>')
def checkout(key):
    current_time = datetime.now()
    request_doc = next(db.collection('requests').where('key', '==', key).limit(1).stream(), None)

    if not request_doc:
        return "Invalid checkout key", 404

    request_data = request_doc.to_dict()

    # Compute duration if generated_at exists
    generated_at_str = request_data.get('generated_at')
    duration_seconds = None
    if generated_at_str:
        try:
            gen_dt = datetime.fromisoformat(generated_at_str)
            duration_seconds = (current_time - gen_dt).total_seconds()
        except Exception:
            duration_seconds = None

    update_fields = {
        'checkedout': True,
        'checkouttime': current_time.strftime('%H:%M:%S'),
        'scanned_at': current_time.isoformat()
    }
    if duration_seconds is not None:
        update_fields['duration_seconds'] = duration_seconds

    db.collection('requests').document(request_doc.id).update(update_fields)

    Name = request_data.get('name')
    id = request_data.get('student_id')
    subject = "Your Ward Checked Out"
    sender = "poppingaming1@gmail.com"
    recipients = ["pingalipraneeth1@gmail.com"]
    body = f"Your Ward '{Name}' '{id}' has checked out University at {current_time.strftime('%H:%M:%S')}."
    send_email(subject, sender, recipients, body)
    return redirect('/cam')


def send_email(subject, sender, recipients, body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = body
    mail.send(msg)

@app.route('/stats', methods=['GET', 'POST'])
def stats():
    return render_template('stats.html', message="Statistics feature temporarily disabled")

@app.route('/stats2', methods=['GET', 'POST'])
def stats2():
    return redirect(url_for('stats'))

@app.route('/wrong')
def wrong():
    session["login_type"] = 'wrongggg'
    return render_template('wrong.html')

@app.route('/cam')
def index():
    return render_template('cam.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('qr_scanned')
def handle_qr_scanned(data):
    print('QR Code Scanned:', data['data'])


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)

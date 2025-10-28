# Debugging Faculty Request Issues

## Steps to Test:

1. **Start the Flask app:**
   ```bash
   python app.py
   ```

2. **Login as faculty** and submit a request

3. **Check the console output** for:
   - "Faculty request saved: {data}" - means it worked
   - Any error messages

4. **Check Firestore directly:**
   - Go to Firebase Console
   - Navigate to Firestore Database
   - Look in the 'requests' collection
   - Filter by `type == 'faculty'`

## Common Issues:

### Issue 1: Firebase not initialized
**Symptom:** Error about firebase_admin module
**Solution:** Install dependencies:
```bash
pip install firebase-admin
```

### Issue 2: Form not submitting
**Symptom:** Page refreshes but nothing happens
**Solution:** Check browser console (F12) for JavaScript errors

### Issue 3: Session not set
**Symptom:** Redirects to login page
**Solution:** Ensure you're logged in as faculty type

### Issue 4: Firestore permissions
**Symptom:** Permission denied errors
**Solution:** Check Firebase rules allow writes to 'requests' collection

## What Should Happen:

1. Faculty fills out the form with a reason
2. Clicks "Submit Request"
3. Request is saved to Firestore with:
   - student_id: faculty username
   - name: faculty name
   - reason: provided reason
   - status: 'Pending'
   - type: 'faculty'
   - priority: calculated from reason text
   - datetime: current date
4. Page redirects back to faculty dashboard
5. Request appears in "My Requests" table
6. HOD can see it in "Faculty Requests" section

## Verify in Code:

The request should be saved at line ~332 in app.py:
```python
db.collection('requests').add(request_data)
```

Check console for: "Faculty request saved: {request_data}"

# app.py
from flask import Flask, render_template, request, redirect, session, url_for
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"

# -------------------------
# LOGIN PAGE
# -------------------------
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']
        role = request.form['role']

        try:
            api_url = "http://127.0.0.1:8000/api/login"
            response = requests.post(api_url, json={
                "email": email,
                "password": password
            })

            data = response.json()

            if response.status_code == 200 and data.get("token"):
                session['token'] = data['token']
                session['role'] = data['user']['role']
                session['username'] = data['user']['name']
                session['user_id'] = data['user']['id']
                return redirect(url_for('dashboard'))
            else:
                error_msg = data.get("detail") or "Invalid credentials"
                return render_template('login.html', error=error_msg)

        except Exception as e:
            return render_template('login.html', error=str(e))

    return render_template('login.html')


# -------------------------
# DASHBOARD PAGE
# -------------------------
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'token' not in session:
        return redirect(url_for('login'))

    results = []
    error = None

    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            try:
                api_url = "http://127.0.0.1:5000/api/search"
                params = {
                    "query": query,
                    "user_id": session['user_id'],
                    "top_n": 10,
                    "search_type": "semantic"
                }

                response = requests.get(api_url, params=params)
                response.raise_for_status()
                results = response.json()

            except requests.exceptions.HTTPError as e:
                error = f"HTTP error: {e.response.status_code} {e.response.text}"
            except requests.exceptions.RequestException as e:
                error = f"Request failed: {str(e)}"
            except ValueError:
                error = "Invalid response received from server"

    return render_template('dashboard.html', results=results, error=error)


# -------------------------
# ADD NOTE (both teachers and students can add)
# -------------------------
@app.route('/addnote', methods=['GET', 'POST'])
def addnote():
    if 'token' not in session:
        return redirect(url_for('login'))
    # Both students and teachers can add notes now

    error = None
    message = None

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        file_path = request.form.get('file_path')
        subject_id = request.form.get('subject_id')
        subject_name = request.form.get('subject_name')

        if not title or not description or not file_path:
            error = "Title, Description, and File Path are required."
        elif not subject_id and not subject_name:
            error = "Either Subject ID or Subject Name is required."
        else:
            try:
                api_url = "http://127.0.0.1:5001/api/addNote"
                headers = {"Authorization": f"Bearer {session['token']}"}
                payload = {
                    "title": title,
                    "description": description,
                    "file_path": file_path
                }
                
                # Add subject_id or subject_name
                if subject_id:
                    payload["subject_id"] = int(subject_id)
                if subject_name:
                    payload["subject_name"] = subject_name
                
                response = requests.post(api_url, json=payload, headers=headers)
                data = response.json()

                if response.status_code == 201:
                    message = data.get("message", "Note added successfully")
                else:
                    error = data.get("error", "Error adding note")

            except Exception as e:
                error = str(e)

    return render_template('addnote.html', error=error, message=message)


# -------------------------
# DELETE NOTE (teachers only)
# -------------------------
@app.route('/deletenote', methods=['GET', 'POST'])
def deletenote():
    if 'token' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'teacher':
        return redirect(url_for('dashboard'))

    error = None
    message = None

    if request.method == 'POST':
        note_id = request.form.get('note_identifier')

        if not note_id:
            error = "Note ID is required."
        else:
            try:
                api_url = f"http://127.0.0.1:5001/api/deleteNote/{note_id}"
                headers = {"Authorization": f"Bearer {session['token']}"}
                response = requests.delete(api_url, headers=headers)
                data = response.json()

                if response.status_code == 200:
                    message = data.get("message", "Note deleted successfully")
                else:
                    error = data.get("error", "Error deleting note")

            except Exception as e:
                error = str(e)

    return render_template('deletenote.html', error=error, message=message)


# -------------------------
# LOGOUT
# -------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, port=5002)
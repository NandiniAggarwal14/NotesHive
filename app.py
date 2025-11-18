# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from functools import wraps
import os
import re
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import socket

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Load the sentence transformer model for semantic search
try:
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Semantic search model loaded successfully!")
except Exception as e:
    print(f"⚠️ Warning: Could not load semantic search model: {e}")
    embedding_model = None

# Helper function to convert Google Drive sharing link to direct download link
def convert_gdrive_link(link):
    """Convert Google Drive sharing link to direct download/view link"""
    if not link or 'drive.google.com' not in link:
        return None
    
    # Extract file ID from various Google Drive URL formats
    patterns = [
        r'/file/d/([a-zA-Z0-9_-]+)',
        r'id=([a-zA-Z0-9_-]+)',
        r'/folders/([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, link)
        if match:
            file_id = match.group(1)
            return {
                'file_id': file_id,
                'view_url': f'https://drive.google.com/file/d/{file_id}/view',
                'download_url': f'https://drive.google.com/uc?export=download&id={file_id}',
                'preview_url': f'https://drive.google.com/file/d/{file_id}/preview'
            }
    
    return None

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Nandini.14",
        database="notehive"
    )

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'student')
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM user WHERE email = %s"
        
        try:
            cursor.execute(query, (email,))
            user = cursor.fetchone()
        except mysql.connector.Error as e:
            cursor.close()
            connection.close()
            flash(f'Database error: {str(e)}', 'error')
            return render_template('login.html')
        
        cursor.close()
        connection.close()
        
        if user:
            # Direct password comparison (plain text)
            if user['password'] == password:
                if user.get('role') == role:
                    session['user_id'] = user['user_id']
                    session['username'] = user.get('name') or user.get('email')
                    session['role'] = user['role']
                    
                    flash(f'Welcome!', 'success')
                    
                    if role == 'teacher':
                        return redirect(url_for('teacher_dashboard'))
                    else:
                        return redirect(url_for('dashboard'))
                else:
                    flash('Invalid role selected', 'error')
            else:
                flash('Invalid email or password', 'error')
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Teacher required decorator
def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'teacher':
            flash('Access denied. Teacher privileges required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')
    role = session.get('role')
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Students see all notes, teachers see only their own
    if role == 'student':
        query = """
            SELECT n.*, u.email as author_email 
            FROM note n 
            JOIN user u ON n.uploaded_by = u.user_id 
            ORDER BY n.note_id DESC
        """
        cursor.execute(query)
    else:
        query = "SELECT * FROM note WHERE uploaded_by = %s ORDER BY note_id DESC"
        cursor.execute(query, (user_id,))
    
    notes = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return render_template('dashboard.html', notes=notes)

@app.route('/add-note', methods=['GET', 'POST'])
@login_required
def add_note():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        keywords = request.form.get('keywords', '')
        file = request.files.get('file')
        gdrive_link = request.form.get('gdrive_link', '').strip()
        
        file_path = None
        
        # Check if Google Drive link is provided
        if gdrive_link:
            gdrive_data = convert_gdrive_link(gdrive_link)
            if gdrive_data:
                # Store the Google Drive link as file_path with a special prefix
                file_path = f"gdrive:{gdrive_link}"
            else:
                flash('Invalid Google Drive link. Please check the URL.', 'error')
                return render_template('addnote.html')
        # Otherwise check for file upload
        elif file and file.filename:
            upload_folder = 'uploads'
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, file.filename)
            file.save(file_path)
        
        connection = get_db_connection()
        cursor = connection.cursor()
        query = """
            INSERT INTO note (title, description, file_path, uploaded_by) 
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (title, description, file_path, session['user_id']))
        connection.commit()
        cursor.close()
        connection.close()
        
        flash('Note created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('addnote.html')

@app.route('/edit-note/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        gdrive_link = request.form.get('gdrive_link', '').strip()
        file = request.files.get('file')
        
        # Get existing note
        query = "SELECT * FROM note WHERE note_id = %s AND uploaded_by = %s"
        cursor.execute(query, (note_id, session['user_id']))
        existing_note = cursor.fetchone()
        
        file_path = existing_note['file_path']  # Keep existing by default
        
        # Update file_path if new link or file provided
        if gdrive_link:
            gdrive_data = convert_gdrive_link(gdrive_link)
            if gdrive_data:
                file_path = f"gdrive:{gdrive_link}"
            else:
                flash('Invalid Google Drive link.', 'error')
                cursor.close()
                connection.close()
                return render_template('addnote.html', note=existing_note)
        elif file and file.filename:
            upload_folder = 'uploads'
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, file.filename)
            file.save(file_path)
        
        query = """
            UPDATE note 
            SET title = %s, description = %s, file_path = %s 
            WHERE note_id = %s AND uploaded_by = %s
        """
        cursor.execute(query, (title, description, file_path, note_id, session['user_id']))
        connection.commit()
        cursor.close()
        connection.close()
        
        flash('Note updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    query = "SELECT * FROM note WHERE note_id = %s AND uploaded_by = %s"
    cursor.execute(query, (note_id, session['user_id']))
    note = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if not note:
        flash('Note not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Parse Google Drive link if exists
    if note.get('file_path') and note['file_path'].startswith('gdrive:'):
        note['gdrive_link'] = note['file_path'].replace('gdrive:', '')
    
    return render_template('addnote.html', note=note)

@app.route('/view-note/<int:note_id>')
@login_required
def view_note(note_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Both students and teachers can view all notes
    query = "SELECT n.*, u.email as author_email FROM note n JOIN user u ON n.uploaded_by = u.user_id WHERE n.note_id = %s"
    cursor.execute(query, (note_id,))
    
    note = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if not note:
        flash('Note not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Parse Google Drive link (with or without prefix)
    if note.get('file_path'):
        file_path = note['file_path']
        if file_path.startswith('gdrive:'):
            gdrive_link = file_path.replace('gdrive:', '')
            gdrive_data = convert_gdrive_link(gdrive_link)
            if gdrive_data:
                note['gdrive_data'] = gdrive_data
                note['is_gdrive'] = True
        elif 'drive.google.com' in file_path:
            # Handle legacy links without gdrive: prefix
            gdrive_data = convert_gdrive_link(file_path)
            if gdrive_data:
                note['gdrive_data'] = gdrive_data
                note['is_gdrive'] = True
        else:
            note['is_gdrive'] = False
    else:
        note['is_gdrive'] = False
    
    return render_template('viewnote.html', note=note)

@app.route('/download-file/<int:note_id>')
@login_required
def download_file(note_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Allow everyone to download any file
    query = "SELECT file_path FROM note WHERE note_id = %s"
    cursor.execute(query, (note_id,))
    
    note = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if note and note['file_path']:
        file_path = note['file_path']
        
        # Check if it's a Google Drive link (with or without prefix)
        if file_path.startswith('gdrive:'):
            gdrive_link = file_path.replace('gdrive:', '')
            gdrive_data = convert_gdrive_link(gdrive_link)
            if gdrive_data:
                return redirect(gdrive_data['download_url'])
            else:
                flash('Invalid Google Drive link', 'error')
                return redirect(url_for('dashboard'))
        elif 'drive.google.com' in file_path:
            # Handle legacy links without gdrive: prefix
            gdrive_data = convert_gdrive_link(file_path)
            if gdrive_data:
                return redirect(gdrive_data['download_url'])
            else:
                flash('Invalid Google Drive link', 'error')
                return redirect(url_for('dashboard'))
        else:
            # Regular file download
            try:
                return send_file(file_path, as_attachment=True)
            except Exception as e:
                flash(f'Error downloading file: {str(e)}', 'error')
                return redirect(url_for('dashboard'))
    
    flash('File not found', 'error')
    return redirect(url_for('dashboard'))

@app.route('/search', methods=['POST'])
@login_required
def search():
    query_text = request.form.get('query', '').strip()
    
    if not query_text:
        flash('Please enter a search term', 'warning')
        return redirect(url_for('dashboard'))
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Step 1: Keyword Search (exact matches)
    search_pattern = f"%{query_text}%"
    keyword_query = """
        SELECT n.*, u.email as author_email 
        FROM note n 
        JOIN user u ON n.uploaded_by = u.user_id 
        WHERE n.title LIKE %s OR n.description LIKE %s
        ORDER BY n.note_id DESC
    """
    cursor.execute(keyword_query, (search_pattern, search_pattern))
    keyword_results = cursor.fetchall()
    
    # Step 2: Semantic Search (meaning-based matches)
    semantic_results = []
    if embedding_model:
        try:
            # Get all notes
            all_notes_query = """
                SELECT n.*, u.email as author_email 
                FROM note n 
                JOIN user u ON n.uploaded_by = u.user_id 
            """
            cursor.execute(all_notes_query)
            all_notes = cursor.fetchall()
            
            if all_notes:
                # Create embeddings for search query
                query_embedding = embedding_model.encode([query_text])[0]
                
                # Create embeddings for all notes and calculate similarity
                note_scores = []
                for note in all_notes:
                    note_content = f"{note['title']} {note['description']}"
                    note_embedding = embedding_model.encode([note_content])[0]
                    
                    # Calculate cosine similarity
                    similarity = cosine_similarity(
                        [query_embedding], 
                        [note_embedding]
                    )[0][0]
                    
                    note_scores.append({
                        'note': note,
                        'similarity': similarity
                    })
                
                # Sort by similarity and get top matches (similarity > 0.3 threshold)
                note_scores.sort(key=lambda x: x['similarity'], reverse=True)
                semantic_results = [
                    item['note'] for item in note_scores 
                    if item['similarity'] > 0.3
                ][:10]  # Top 10 semantic matches
        
        except Exception as e:
            print(f"Semantic search error: {e}")
            # Fall back to keyword search only
            pass
    
    cursor.close()
    connection.close()
    
    # Step 3: Combine and deduplicate results
    # Keyword results first (exact matches), then semantic results
    combined_results = []
    seen_ids = set()
    
    # Add keyword results first
    for note in keyword_results:
        if note['note_id'] not in seen_ids:
            combined_results.append(note)
            seen_ids.add(note['note_id'])
    
    # Add semantic results
    for note in semantic_results:
        if note['note_id'] not in seen_ids:
            combined_results.append(note)
            seen_ids.add(note['note_id'])
    
    # Flash appropriate message
    if combined_results:
        keyword_count = len(keyword_results)
        semantic_count = len(semantic_results)
        
        if keyword_count > 0 and semantic_count > 0:
            flash(f'Found {len(combined_results)} note(s): {keyword_count} exact matches + {semantic_count} related matches for "{query_text}"', 'success')
        elif keyword_count > 0:
            flash(f'Found {keyword_count} exact match(es) for "{query_text}"', 'success')
        else:
            flash(f'Found {semantic_count} related note(s) for "{query_text}"', 'success')
    else:
        flash(f'No notes found matching "{query_text}"', 'warning')
    
    return render_template('dashboard.html', notes=combined_results, search_query=query_text)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        email = request.form.get('email', '').strip()
        role = request.form.get('role', '')
        
        # Validate inputs
        if not username or not password or not email or not role:
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        if len(username) < 2:
            flash('Name must be at least 2 characters', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template('register.html')
        
        if '@' not in email:
            flash('Please enter a valid email address', 'error')
            return render_template('register.html')
        
        if role not in ['student', 'teacher']:
            flash('Please select a valid role', 'error')
            return render_template('register.html')
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            # Check if email already exists
            check_query = "SELECT email FROM user WHERE email = %s"
            cursor.execute(check_query, (email,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                cursor.close()
                connection.close()
                flash('This email is already registered. Please use a different email or login.', 'error')
                return render_template('register.html')
            
            # Insert new user - using 'name' column instead of 'username'
            # Based on your database schema, the column is likely 'name' not 'username'
            insert_query = "INSERT INTO user (name, password, email, role) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (username, password, email, role))
            connection.commit()
            cursor.close()
            connection.close()
            
            flash(f'Registration successful! You can now login as a {role}.', 'success')
            return redirect(url_for('login'))
            
        except mysql.connector.Error as e:
            # More detailed error message
            error_msg = str(e)
            if 'Unknown column' in error_msg:
                flash('Database configuration error. Please contact administrator.', 'error')
                print(f"Database error: {error_msg}")  # For debugging
            else:
                flash(f'Database error: {error_msg}', 'error')
            return render_template('register.html')
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/teacher/dashboard')
@teacher_required
def teacher_dashboard():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # Removed ORDER BY created_at, using note_id instead
    query = """
        SELECT n.*, u.email as username 
        FROM note n 
        JOIN user u ON n.uploaded_by = u.user_id 
        ORDER BY n.note_id DESC
    """
    cursor.execute(query)
    all_notes = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return render_template('teacher_dashboard.html', notes=all_notes)

@app.route('/delete-note/<int:note_id>', methods=['GET', 'POST'])
@login_required
@teacher_required
def delete_note(note_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Teachers can delete any note
    query = "SELECT * FROM note WHERE note_id = %s"
    cursor.execute(query, (note_id,))
    note = cursor.fetchone()
    
    if not note:
        cursor.close()
        connection.close()
        flash('Note not found', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        query = "DELETE FROM note WHERE note_id = %s"
        cursor.execute(query, (note_id,))
        connection.commit()
        cursor.close()
        connection.close()
        
        flash('Note deleted successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    cursor.close()
    connection.close()
    return render_template('deletenote.html', note=note)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

def find_available_port(host='127.0.0.1', ports=(5000,5001,5002)):
    for p in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((host, p))
            s.close()
            return p
        except OSError:
            s.close()
    return None

if __name__ == '__main__':
    preferred_host = '127.0.0.1'
    preferred_ports = (5000, 5001, 5002)
    port = find_available_port(preferred_host, preferred_ports)
    if port is None:
        print("ERROR: No available ports found in", preferred_ports)
        print(" - Check for processes using these ports: netstat -ano | findstr :5000")
        print(" - Run terminal as Administrator or free the port and retry.")
    else:
        print(f"Starting NotesHive on http://{preferred_host}:{port}")
        app.run(debug=True, host=preferred_host, port=port)
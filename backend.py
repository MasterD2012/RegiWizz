from flask import Flask, request, jsonify, session, render_template
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'

# Database file
DATABASE = 'app.db'

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # Register table
    c.execute('''
        CREATE TABLE IF NOT EXISTS register (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            status TEXT NOT NULL,
            session_notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Sign-up endpoint
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required."})

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Check if username exists
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    if c.fetchone():
        conn.close()
        return jsonify({"success": False, "message": "Username already exists."})

    # Insert new user
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "User registered successfully."})

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Authenticate user
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        session['user_id'] = user[0]
        session['username'] = user[1]
        return jsonify({"success": True, "message": "Login successful."})
    else:
        return jsonify({"success": False, "message": "Invalid username or password."})

# Logout endpoint
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully."})

# Get register data
@app.route('/register', methods=['GET'])
def get_register():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Unauthorized access."}), 401

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM register")
    register = c.fetchall()
    conn.close()

    return jsonify({"success": True, "register": register})

# Add or update register data
@app.route('/register', methods=['POST'])
def update_register():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Unauthorized access."}), 401

    data = request.json
    student_name = data.get('student_name')
    status = data.get('status')
    session_notes = data.get('session_notes', '')

    if not student_name or not status:
        return jsonify({"success": False, "message": "Student name and status are required."})

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Check if the student already exists
    c.execute("SELECT * FROM register WHERE student_name=?", (student_name,))
    existing = c.fetchone()

    if existing:
        # Update the record
        c.execute("UPDATE register SET status=?, session_notes=? WHERE student_name=?", 
                  (status, session_notes, student_name))
    else:
        # Insert new record
        c.execute("INSERT INTO register (student_name, status, session_notes) VALUES (?, ?, ?)", 
                  (student_name, status, session_notes))
    
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Register updated successfully."})

# Cloud save (for demonstration purposes, use local storage here)
@app.route('/cloud-save', methods=['POST'])
def cloud_save():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Unauthorized access."}), 401

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM register")
    register = c.fetchall()
    conn.close()

    # Simulate saving to the cloud
    file_path = os.path.join('cloud_backup', f'register_backup_user_{session["user_id"]}.txt')
    os.makedirs('cloud_backup', exist_ok=True)
    with open(file_path, 'w') as f:
        for record in register:
            f.write(f'{record}\n')

    return jsonify({"success": True, "message": "Register saved to the cloud successfully."})

# Main route (redirect to login)
@app.route('/')
def index():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)

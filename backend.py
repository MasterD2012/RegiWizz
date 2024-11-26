from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# In-memory database for simplicity
DATABASE = 'register.db'


def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS register (name TEXT, previous_session TEXT, mark TEXT)''')
    conn.commit()
    conn.close()


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username, password = data.get('username'), data.get('password')

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({"success": True})
    return jsonify({"success": False})


@app.route('/get-register', methods=['GET'])
def get_register():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM register")
    data = [{"name": row[0], "previousSession": row[1], "mark": row[2]} for row in c.fetchall()]
    conn.close()
    return jsonify(data)


@app.route('/save-register', methods=['POST'])
def save_register():
    register_data = request.json
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM register")  # Clear existing data
    for student in register_data:
        c.execute("INSERT INTO register (name, previous_session, mark) VALUES (?, ?, ?)",
                  (student['name'], student['previousSession'], student['mark']))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


if __name__ == '__main__':
    init_db()
    app.r
    un(debug=True)

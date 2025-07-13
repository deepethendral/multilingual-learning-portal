from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash
import os
import sqlite3
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.secret_key = 'sih2025'
UPLOAD_FOLDER = 'content'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ---------- DB Connection ----------
def get_db_connection():
    conn = sqlite3.connect('database/users.db')
    conn.row_factory = sqlite3.Row
    return conn

# ---------- Routes ----------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))
        return "Invalid credentials!"
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    language = request.args.get('lang', 'hi')
    files_path = os.path.join(app.config['UPLOAD_FOLDER'], language)

    try:
        files = os.listdir(files_path)
    except FileNotFoundError:
        files = []

    return render_template('dashboard.html',
                           username=session['username'],
                           language=language,
                           files=files)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        language = request.form['language']
        uploaded_file = request.files['file']

        if uploaded_file and uploaded_file.filename:
            lang_folder = os.path.join(app.config['UPLOAD_FOLDER'], language)
            os.makedirs(lang_folder, exist_ok=True)

            # Save file with unique name to avoid overwrite
            unique_filename = f"{uuid.uuid4().hex}_{secure_filename(uploaded_file.filename)}"
            uploaded_file.save(os.path.join(lang_folder, unique_filename))

            flash("File uploaded successfully!")
            return redirect(url_for('dashboard', lang=language))

    return render_template('upload.html')


@app.route('/download/<lang>/<filename>')
def download_file(lang, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], lang), filename, as_attachment=True)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    questions = [
        {"text": "What is the capital of India?", "options": ["Delhi", "Mumbai", "Chennai"], "answer": "Delhi"},
        {"text": "What is 2 + 2?", "options": ["3", "4", "5"], "answer": "4"}
    ]

    if request.method == 'POST':
        score = 0
        for i, q in enumerate(questions):
            selected = request.form.get(f'q{i}')
            if selected == q['answer']:
                score += 1
        return render_template('quiz.html', questions=questions, score=score, total=len(questions))

    return render_template('quiz.html', questions=questions)


if __name__ == '__main__':
    app.run(debug=True)
# Ensure the content directory exists
from flask import Flask, render_template, request, redirect, session, url_for, flash, abort
from flask_mail import Mail, Message
from html import escape
import sqlite3
import os
from functools import wraps
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import json
import urllib.request

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path, override=True)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

def env_flag(name, default):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}

app.config.update(
    MAIL_SERVER=os.environ.get('MAIL_SERVER', 'smtp.gmail.com'),
    MAIL_PORT=int(os.environ.get('MAIL_PORT') or 587),
    MAIL_USE_TLS=env_flag('MAIL_USE_TLS', True),
    MAIL_USE_SSL=env_flag('MAIL_USE_SSL', False),
    MAIL_USERNAME=os.environ.get('SMTP_USERNAME') or os.environ.get('EMAIL_ADMIN'),
    MAIL_PASSWORD=os.environ.get('SMTP_PASSWORD') or os.environ.get('EMAIL_PASS'),
    MAIL_DEFAULT_SENDER=os.environ.get('EMAIL_DEFAULT_SENDER'),
    RESEND_API_KEY=os.environ.get('RESEND_API_KEY'),
    GRIEVANCE_NOTIFICATION_EMAIL=os.environ.get(
        'GRIEVANCE_NOTIFICATION_EMAIL', 'azizbennacer9@gmail.com'),
)

mail = Mail(app)


def send_email_safely(message):
    try:
        api_key = app.config.get('RESEND_API_KEY')
        if api_key:
            payload = {
                'from': message.sender or app.config['MAIL_DEFAULT_SENDER'],
                'to': message.recipients,
                'subject': message.subject,
            }
            if message.html:
                payload['html'] = message.html
            if message.body:
                payload['text'] = message.body
            api_request = urllib.request.Request(
                'https://api.resend.com/emails',
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json',
                },
                method='POST',
            )
            with urllib.request.urlopen(api_request, timeout=10):
                return True
        mail.send(message)
    except Exception as error:
        app.logger.error('Email notification failed: %s', type(error).__name__)
        return False
    return True

USER_NAME = os.environ.get('USER_NAME')
USER_PASSWORD = os.environ.get('USER_PASSWORD')
ADMIN_NAME = os.environ.get('ADMIN_NAME')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
PORTAL_URL = os.environ.get('PORTAL_URL')
USER_STATUS_OPTIONS = (
    'Still bothering me',
    'Getting better',
    'Getting worse',
    'Already resolved',
)
MOOD_OPTIONS = (
    ('Frustrated', '😤'),
    ('Angry', '😠'),
    ('Sad', '😢'),
    ('Playful', '😏'),
)
PRIORITY_OPTIONS = (
    ('A small thing', '🟢'),
    ('Worth a chat', '🟡'),
    ('This matters to me', '🟠'),
    ('Can we talk soon?', '🔴'),
)

@app.context_processor
def inject_navigation_state():
    current_user = session.get('user')
    return {
        'is_logged_in': current_user is not None,
        'is_portal_user': current_user is not None and current_user == USER_NAME,
        'is_admin': current_user is not None and current_user == ADMIN_NAME,
    }

def init_db():
    with sqlite3.connect('grievances.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS grievances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                mood TEXT,
                priority TEXT,
                resolved INTEGER DEFAULT 0,
                response TEXT DEFAULT ''
            )
        ''')
        columns = {row[1] for row in c.execute('PRAGMA table_info(grievances)')}
        if 'user_status' not in columns:
            c.execute("ALTER TABLE grievances ADD COLUMN user_status TEXT NOT NULL DEFAULT 'Still bothering me'")
        conn.commit()

def login_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if 'user' not in session or session.get('user') != role:
                return redirect(url_for('login'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

@app.route('/')
def home():
    return render_template('home.html', user_display_name=USER_NAME)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        if user == USER_NAME and pw == USER_PASSWORD:
            session['user'] = USER_NAME
            return redirect(url_for('submit'))
        elif user == ADMIN_NAME and pw == ADMIN_PASSWORD:
            session['user'] = ADMIN_NAME
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html', user_display_name=USER_NAME)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/submit', methods=['GET', 'POST'])
@login_required(USER_NAME)
def submit():
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['description']
        mood = request.form['mood']
        priority = request.form['priority']
        user_status = request.form.get('user_status', '')
        if user_status not in USER_STATUS_OPTIONS:
            flash('Please choose how things are going now.', 'error')
            return redirect(url_for('submit'))
        with sqlite3.connect('grievances.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO grievances (title, description, mood, priority, user_status) VALUES (?, ?, ?, ?, ?)",
                      (title, desc, mood, priority, user_status))
            conn.commit()
            grievance_id = c.lastrowid

        portal_url = (PORTAL_URL or request.url_root).rstrip('/')
        login_url = f"{portal_url}{url_for('login')}"
        safe_desc = escape(desc).replace('\n', '<br>')
        msg = Message("New Grievance from {} 💌".format(USER_NAME),
                      sender=app.config['MAIL_DEFAULT_SENDER'],
                      recipients=[app.config['GRIEVANCE_NOTIFICATION_EMAIL']])
        msg.html = f"""
            <h3>New Grievance Submitted 💌</h3>
            <p><strong>Title:</strong> {escape(title)}</p>
            <p><strong>Mood:</strong> {escape(mood)}</p>
            <p><strong>Priority:</strong> {escape(priority)}</p>
            <p><strong>How things are going:</strong> {escape(user_status)}</p>
            <p><strong>Description:</strong><br>{safe_desc}</p>
            <hr>
            <p><a href="{escape(login_url, quote=True)}">Open the portal to respond 💌</a></p>
        """

        if send_email_safely(msg):
            flash('Your note is saved, and {} has been notified 💌'.format(ADMIN_NAME), 'success')
        else:
            flash('Your note is saved in the Admin Desk, but the email notification could not be sent. Check the configured admin email and mail settings.', 'warning')
        return redirect(url_for('thank_you'))

    return render_template('submit.html')

def send_email_to_user(grievance_id, response):
    with sqlite3.connect('grievances.db') as conn:
        c = conn.cursor()
        c.execute("SELECT title, priority, resolved FROM grievances WHERE id = ?", (grievance_id,))
        result = c.fetchone()

    if result:
        title, priority, resolved = result
        status = "Resolved ✅" if resolved == 1 else "Pending ❌"

        # Create the email message
        msg = Message("Grievance Response Received - Re: {}".format(title),
                    recipients=[os.environ.get('EMAIL_USER_RECEIVER')])

        safe_response = escape(response).replace('\n', '<br>')
        msg.html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; color: #333;">
                <div style="background-color: #fff; padding: 20px; border-radius: 8px; width: 600px; margin: auto; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
                    <h2 style="color: #4CAF50;">Grievance Response Received</h2>
                    <p><strong>Title:</strong> {escape(title)}</p>
                    <p><strong>Priority:</strong> {escape(priority)}</p>
                    <p><strong>Status:</strong> {status}</p>
                    <hr>
                    <p><strong>Your Response:</strong></p>
                    <p style="background-color: #f9f9f9; padding: 10px; border-left: 4px solid #4CAF50; font-style: italic;">
                        {safe_response}
                    </p>
                    <br>
                    <p style="color: #888;">This is an automated message from the Grievance Portal. Please do not reply.</p>
                </div>
            </body>
        </html>
        """

        return send_email_safely(msg)
    return False

@app.route('/thankyou')
@login_required(USER_NAME)
def thank_you():
    return render_template('thankyou.html', user_display_name=USER_NAME, admin_display_name=ADMIN_NAME)

@app.route('/my_grievances')
@login_required(USER_NAME)
def my_grievances():
    with sqlite3.connect('grievances.db') as conn:
        c = conn.cursor()
        c.execute("SELECT title, description, mood, priority, response, resolved, user_status, id FROM grievances")
        data = c.fetchall()
    return render_template('my_grievances.html', grievances=data, status_options=USER_STATUS_OPTIONS)

def notify_note_update(title, user_status, changes):
    portal_url = (PORTAL_URL or request.url_root).rstrip('/')
    login_url = f"{portal_url}{url_for('login')}"
    msg = Message("Note updated by {} 💌".format(USER_NAME),
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[app.config['GRIEVANCE_NOTIFICATION_EMAIL']])
    msg.html = f"""
        <h3>A note was updated 💌</h3>
        <p><strong>Title:</strong> {escape(title)}</p>
        <p><strong>How things are going now:</strong> {escape(user_status)}</p>
        <p><strong>Changed:</strong> {escape(', '.join(changes))}</p>
        <hr>
        <p><a href="{escape(login_url, quote=True)}">Open the portal 💌</a></p>
    """
    return send_email_safely(msg)

def flash_update_result(emailed):
    if emailed:
        flash('Your note is updated, and {} has been notified 💌'.format(ADMIN_NAME), 'success')
    else:
        flash('Your note is updated, but the email notification could not be sent.', 'warning')

@app.route('/update_status/<int:gid>', methods=['POST'])
@login_required(USER_NAME)
def update_status(gid):
    user_status = request.form.get('user_status', '')
    if user_status not in USER_STATUS_OPTIONS:
        flash('Please choose a valid update.', 'error')
        return redirect(url_for('my_grievances'))
    with sqlite3.connect('grievances.db') as conn:
        c = conn.cursor()
        c.execute("SELECT title, user_status FROM grievances WHERE id = ?", (gid,))
        row = c.fetchone()
        if row is None:
            abort(404)
        if row[1] == user_status:
            flash('That was already your update.', 'success')
            return redirect(url_for('my_grievances'))
        c.execute("UPDATE grievances SET user_status = ? WHERE id = ?", (user_status, gid))
        conn.commit()
    flash_update_result(notify_note_update(row[0], user_status, ['status']))
    return redirect(url_for('my_grievances'))

@app.route('/edit/<int:gid>', methods=['GET', 'POST'])
@login_required(USER_NAME)
def edit_note(gid):
    with sqlite3.connect('grievances.db') as conn:
        c = conn.cursor()
        c.execute("SELECT title, description, mood, priority, user_status FROM grievances WHERE id = ?", (gid,))
        row = c.fetchone()
        if row is None:
            abort(404)
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            desc = request.form.get('description', '').strip()
            mood = request.form.get('mood', '')
            priority = request.form.get('priority', '')
            user_status = request.form.get('user_status', '')
            valid = (title and desc and len(title) <= 120
                     and mood in dict(MOOD_OPTIONS)
                     and priority in dict(PRIORITY_OPTIONS)
                     and user_status in USER_STATUS_OPTIONS)
            if not valid:
                flash('Please fill in every field with a valid choice.', 'error')
                return redirect(url_for('edit_note', gid=gid))
            changes = [label for label, old, new in (
                ('title', row[0], title), ('description', row[1], desc),
                ('mood', row[2], mood), ('importance', row[3], priority),
                ('status', row[4], user_status)) if old != new]
            if not changes:
                flash('Nothing to update.', 'success')
                return redirect(url_for('my_grievances'))
            c.execute("UPDATE grievances SET title = ?, description = ?, mood = ?, priority = ?, user_status = ? WHERE id = ?",
                      (title, desc, mood, priority, user_status, gid))
            conn.commit()
            flash_update_result(notify_note_update(title, user_status, changes))
            return redirect(url_for('my_grievances'))
    note = dict(zip(('title', 'description', 'mood', 'priority', 'user_status'), row), id=gid)
    return render_template('edit_note.html', note=note, status_options=USER_STATUS_OPTIONS,
                           mood_options=MOOD_OPTIONS, priority_options=PRIORITY_OPTIONS)

@app.route('/view_grievances_admin')
@login_required(ADMIN_NAME)
def view_grievances_admin():
    with sqlite3.connect('grievances.db') as conn:
        c = conn.cursor()
        c.execute("SELECT title, description, mood, priority, response, resolved, user_status FROM grievances")
        grievances = c.fetchall()
    return render_template('my_grievances.html', grievances=grievances)

@app.route('/respond/<int:gid>', methods=['POST'])
@login_required(ADMIN_NAME)
def respond(gid):
    response = request.form['response']
    with sqlite3.connect('grievances.db') as conn:
        c = conn.cursor()
        c.execute("UPDATE grievances SET response = ? WHERE id = ?", (response, gid))
        conn.commit()

    if send_email_to_user(gid, response):
        flash('Your response was saved and the user was notified.', 'success')
    else:
        flash('Your response was saved, but its email notification could not be sent. Check the SMTP settings.', 'warning')
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required(ADMIN_NAME)
def dashboard():
    with sqlite3.connect('grievances.db') as conn:
        c = conn.cursor()
        c.execute("SELECT id, title, description, mood, priority, resolved, response, user_status FROM grievances")
        data = c.fetchall()
    return render_template('dashboard.html', grievances=data)

@app.route('/resolve/<int:gid>')
@login_required(ADMIN_NAME)
def resolve(gid):
    with sqlite3.connect('grievances.db') as conn:
        c = conn.cursor()
        c.execute("UPDATE grievances SET resolved = 1 WHERE id = ?", (gid,))
        conn.commit()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_db()
    from waitress import serve

    serve(app, host='127.0.0.1', port=int(os.environ.get('PORT') or 5000))

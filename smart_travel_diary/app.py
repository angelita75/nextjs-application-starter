from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

mail = Mail(app)

from models import User, DiaryEntry, Incident, Comment, AlertPreference

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already exists', 'danger')
            return redirect(url_for('register'))
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/submit_diary', methods=['GET', 'POST'])
@login_required
def submit_diary():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        photo = request.files.get('photo')
        filename = None
        if photo and photo.filename != '':
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        diary_entry = DiaryEntry(title=title, description=description, photo_filename=filename, user_id=current_user.id)
        db.session.add(diary_entry)
        db.session.commit()
        flash('Diary entry submitted successfully.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('submit_diary.html')

@app.route('/view_diaries', methods=['GET'])
def view_diaries():
    search_query = request.args.get('q', '')
    if search_query:
        diary_entries = DiaryEntry.query.filter(
            DiaryEntry.public == True,
            (DiaryEntry.title.ilike(f'%{search_query}%')) | (DiaryEntry.description.ilike(f'%{search_query}%'))
        ).order_by(DiaryEntry.timestamp.desc()).all()
    else:
        diary_entries = DiaryEntry.query.filter_by(public=True).order_by(DiaryEntry.timestamp.desc()).all()
    return render_template('view_diaries.html', diary_entries=diary_entries)

@app.route('/add_comment/<int:diary_id>', methods=['POST'])
@login_required
def add_comment(diary_id):
    content = request.form['content']
    if content:
        comment = Comment(content=content, user_id=current_user.id, diary_entry_id=diary_id)
        db.session.add(comment)
        db.session.commit()
        flash('Comment added.', 'success')
    else:
        flash('Comment cannot be empty.', 'danger')
    return redirect(url_for('view_diaries'))

@app.route('/report_incident', methods=['GET', 'POST'])
@login_required
def report_incident():
    if request.method == 'POST':
        incident_type = request.form['incident_type']
        location = request.form['location']
        description = request.form.get('description')
        photo = request.files.get('photo')
        filename = None
        if photo and photo.filename != '':
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Geocode location using Nominatim API
        import requests
        lat = None
        lon = None
        try:
            response = requests.get('https://nominatim.openstreetmap.org/search', params={
                'q': location,
                'format': 'json'
            }, headers={'User-Agent': 'SmartTravelDiaryApp'})
            data = response.json()
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
        except Exception as e:
            print(f"Geocoding error: {e}")
        incident = Incident(
            incident_type=incident_type,
            location=location,
            latitude=lat,
            longitude=lon,
            description=description,
            photo_filename=filename,
            user_id=current_user.id,
            status='Pending'
        )
        db.session.add(incident)
        db.session.commit()
        flash('Incident reported successfully. Awaiting admin approval.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('report_incident.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    from models import AlertPreference
    alert_pref = AlertPreference.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        username = request.form['username']
        email_alerts = 'email_alerts' in request.form
        # Update username
        current_user.username = username
        # Update or create alert preferences
        if alert_pref:
            alert_pref.email_alerts = email_alerts
        else:
            alert_pref = AlertPreference(user_id=current_user.id, email_alerts=email_alerts)
            db.session.add(alert_pref)
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', alert_pref=alert_pref)

if __name__ == '__main__':
    app.run(debug=True)

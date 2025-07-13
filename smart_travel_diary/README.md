# Smart Travel Diary Platform

## Overview
This is a Flask-based web application for users to submit travel diary entries, report safety incidents, view incidents on a map, and receive real-time risk alerts via email. Admins can moderate content and approve incidents.

## Features
- User registration and login with hashed passwords
- Submit and view travel diary entries with optional photos
- Report safety incidents with location and photos
- View incidents on a Leaflet.js map with OpenStreetMap
- Admin moderation panel for incidents and content
- Email alerts using Flask-Mail with Gmail SMTP

## Setup Instructions

1. Clone the repository or download the project files.

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set environment variables for email (replace with your credentials):
   ```bash
   export MAIL_USERNAME='your_email@gmail.com'
   export MAIL_PASSWORD='your_app_password'
   export SECRET_KEY='your_secret_key'
   ```

5. Initialize the database:
   ```bash
   flask shell
   >>> from app import db
   >>> db.create_all()
   >>> exit()
   ```

6. Run the application:
   ```bash
   flask run
   ```

7. Open your browser and go to `http://localhost:5000`

## Notes
- Use Gmail app password for MAIL_PASSWORD if 2FA is enabled.
- The app uses SQLite for simplicity.
- Leaflet.js and Bootstrap are included via CDN in templates.

## Demo Admin User
- A sample admin user will be created during setup for demo purposes.

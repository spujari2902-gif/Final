"""
Initialize the database with test data
Run this script once to set up the database with sample projects and users
"""
import sys
sys.path.insert(0, '/c/Users/USER/Downloads')

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'construction_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(50))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    status = db.Column(db.String(100))
    budget = db.Column(db.Float)
    spent = db.Column(db.Float)

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if users already exist
        if User.query.first() is None:
            # Create test users with different roles
            users = [
                User(username='store', password=generate_password_hash('password123'), role='Store'),
                User(username='purchase', password=generate_password_hash('password123'), role='Purchase'),
                User(username='execution', password=generate_password_hash('password123'), role='Execution'),
                User(username='accounts', password=generate_password_hash('password123'), role='Accounts'),
                User(username='billing', password=generate_password_hash('password123'), role='Billing'),
            ]
            for user in users:
                db.session.add(user)
            db.session.commit()
            print("✓ Users created")
        
        # Check if projects already exist
        if Project.query.first() is None:
            # Create sample projects
            projects = [
                Project(name='Building A - Foundation', status='In Progress', budget=50000.00, spent=35000.00),
                Project(name='Building B - Framing', status='In Progress', budget=75000.00, spent=42000.00),
                Project(name='Building C - Electrical', status='Planned', budget=60000.00, spent=0.00),
            ]
            for project in projects:
                db.session.add(project)
            db.session.commit()
            print("✓ Projects created")
        
        print("\n✓ Database initialized successfully!")
        print("\nTest Credentials:")
        print("  Username: store  | Password: password123  | Role: Store")
        print("  Username: purchase | Password: password123 | Role: Purchase")
        print("  Username: execution | Password: password123 | Role: Execution")

if __name__ == '__main__':
    init_db()

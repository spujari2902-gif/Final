
from flask import Flask, render_template, redirect, url_for, request, abort, send_from_directory, jsonify # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
import matplotlib.pyplot as plt # type: ignore
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'construction_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# ----------------------------
# Database Models
# ----------------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(50))  # Store, Purchase, Execution, Accounts, Billing


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    status = db.Column(db.String(100))
    budget = db.Column(db.Float)
    spent = db.Column(db.Float)


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    department = db.Column(db.String(100))
    description = db.Column(db.String(500))
    amount = db.Column(db.Float)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ----------------------------
# Routes
# ----------------------------

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            return render_template('login.html', error='Invalid credentials')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        projects = Project.query.all()
        generate_chart(projects)
    except Exception as e:
        print(f"Error loading dashboard: {e}")
        projects = []
    
    return render_template('dashboard.html', projects=projects, role=current_user.role)

@app.route('/add_entry/<int:project_id>', methods=['POST'])
@login_required
def add_entry(project_id):
    try:
        # Validate project exists
        project = Project.query.get(project_id)
        if not project:
            abort(404)
        
        # Validate form data
        description = request.form.get('description', '').strip()
        amount_str = request.form.get('amount', '').strip()
        
        if not description or not amount_str:
            return redirect(url_for('dashboard'))
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                return redirect(url_for('dashboard'))
        except ValueError:
            return redirect(url_for('dashboard'))
        
        # Create entry
        new_entry = Entry(
            project_id=project_id,
            department=current_user.role,
            description=description,
            amount=amount
        )
        db.session.add(new_entry)
        
        # Update project spent
        project.spent += amount
        if project.spent > project.budget:
            project.status = 'Over Budget'
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error adding entry: {e}")
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ----------------------------
# Chart Generator
# ----------------------------

def generate_chart(projects):
    try:
        if not projects:
            return
        
        names = [p.name for p in projects]
        spent = [p.spent for p in projects]
        budgets = [p.budget for p in projects]

        plt.figure(figsize=(10, 6))
        x = range(len(names))
        width = 0.35
        
        plt.bar([i - width/2 for i in x], budgets, width, label='Budget', color='#667eea')
        plt.bar([i + width/2 for i in x], spent, width, label='Spent', color='#764ba2')
        
        plt.xlabel('Projects')
        plt.ylabel('Amount ($)')
        plt.title('Project Budget vs Spent Overview')
        plt.xticks(x, names, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()

        chart_dir = os.path.join(os.path.dirname(__file__), 'static', 'charts')
        if not os.path.exists(chart_dir):
            os.makedirs(chart_dir)

        chart_path = os.path.join(chart_dir, 'chart.png')
        plt.savefig(chart_path, dpi=100, bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"Error generating chart: {e}")
        plt.close()

# ----------------------------
# PWA Support
# ----------------------------

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')

@app.route('/sw.js')
def serve_service_worker():
    return send_from_directory('static', 'sw.js', mimetype='application/javascript')

# ----------------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

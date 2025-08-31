from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import json
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tourism_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Database Models
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    country = db.Column(db.String(50), default='Pakistan')
    website = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    subscription_plan = db.Column(db.String(20), default='basic')  # basic, premium, enterprise
    subscription_expires = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='company', lazy=True, cascade='all, delete-orphan')
    itineraries = db.relationship('Itinerary', backref='company', lazy=True, cascade='all, delete-orphan')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    role = db.Column(db.String(20), default='admin')  # super_admin, admin, editor
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=True)  # Nullable for super_admin

class Itinerary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    
    # Relationships
    stops = db.relationship('Stop', backref='itinerary', lazy=True, cascade='all, delete-orphan')

class Stop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    is_day_active = db.Column(db.Boolean, default=False)
    image_filename = db.Column(db.String(255))
    order_in_day = db.Column(db.Integer, default=1)
    itinerary_id = db.Column(db.Integer, db.ForeignKey('itinerary.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Authentication helpers
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
            
            user = User.query.get(session['user_id'])
            if not user or not user.is_active:
                session.clear()
                flash('Your account is not active.', 'error')
                return redirect(url_for('login'))
            
            if role and user.role != role and user.role != 'super_admin':
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def get_current_company():
    user = get_current_user()
    if user and user.company_id:
        return Company.query.get(user.company_id)
    return None

# Routes

@app.route('/')
def index():
    """Main user interface - displays the map and itinerary"""
    # Get all active itineraries with company information
    itineraries = db.session.query(Itinerary, Company).join(Company).filter(
        Itinerary.is_active == True,
        Company.is_active == True
    ).all()
    return render_template('index.html', itineraries=itineraries)

@app.route('/api/stops/<int:itinerary_id>')
def get_stops(itinerary_id):
    """API endpoint to get all stops for an itinerary"""
    stops = Stop.query.filter_by(itinerary_id=itinerary_id).order_by(Stop.day_number, Stop.order_in_day).all()
    stops_data = []
    for stop in stops:
        stops_data.append({
            'id': stop.id,
            'name': stop.name,
            'description': stop.description,
            'latitude': stop.latitude,
            'longitude': stop.longitude,
            'day_number': stop.day_number,
            'is_day_active': stop.is_day_active,
            'image_filename': stop.image_filename,
            'order_in_day': stop.order_in_day
        })
    return jsonify(stops_data)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email, is_active=True).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['user_role'] = user.role
            session['company_id'] = user.company_id
            
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash(f'Welcome back, {user.first_name}!', 'success')
            
            if user.role == 'super_admin':
                return redirect(url_for('super_admin_dashboard'))
            else:
                return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Company registration"""
    if request.method == 'POST':
        # Company information
        company_name = request.form['company_name']
        company_email = request.form['company_email']
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        city = request.form.get('city', '')
        website = request.form.get('website', '')
        
        # User information
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        user_email = request.form['user_email']
        password = request.form['password']
        
        # Check if company email already exists
        if Company.query.filter_by(email=company_email).first():
            flash('A company with this email already exists.', 'error')
            return render_template('auth/register.html')
        
        # Check if user email already exists
        if User.query.filter_by(email=user_email).first():
            flash('A user with this email already exists.', 'error')
            return render_template('auth/register.html')
        
        try:
            # Create company
            company = Company(
                name=company_name,
                email=company_email,
                phone=phone,
                address=address,
                city=city,
                website=website,
                subscription_plan='basic',
                subscription_expires=datetime.utcnow() + timedelta(days=30)  # 30-day trial
            )
            db.session.add(company)
            db.session.flush()  # Get company ID
            
            # Create admin user
            user = User(
                username=user_email,
                email=user_email,
                password_hash=generate_password_hash(password),
                first_name=first_name,
                last_name=last_name,
                role='admin',
                company_id=company.id
            )
            db.session.add(user)
            db.session.commit()
            
            flash('Company registered successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Super Admin routes
@app.route('/super-admin')
@login_required('super_admin')
def super_admin_dashboard():
    """Super admin dashboard"""
    companies = Company.query.order_by(Company.created_at.desc()).all()
    users = User.query.order_by(User.created_at.desc()).all()
    total_itineraries = Itinerary.query.count()
    total_stops = Stop.query.count()
    
    return render_template('super_admin/dashboard.html', 
                         companies=companies, 
                         users=users,
                         total_itineraries=total_itineraries,
                         total_stops=total_stops)

@app.route('/super-admin/companies')
@login_required('super_admin')
def manage_companies():
    """Manage all companies"""
    companies = Company.query.order_by(Company.created_at.desc()).all()
    return render_template('super_admin/companies.html', companies=companies)

@app.route('/super-admin/company/<int:company_id>/toggle', methods=['POST'])
@login_required('super_admin')
def toggle_company_status(company_id):
    """Toggle company active status"""
    company = Company.query.get_or_404(company_id)
    company.is_active = not company.is_active
    db.session.commit()
    
    status = "activated" if company.is_active else "deactivated"
    flash(f'Company {company.name} has been {status}.', 'success')
    return redirect(url_for('manage_companies'))

# Company Admin routes
@app.route('/admin')
@login_required()
def admin_dashboard():
    """Company admin dashboard"""
    user = get_current_user()
    company = get_current_company()
    
    if not company:
        flash('No company associated with your account.', 'error')
        return redirect(url_for('logout'))
    
    # Get company-specific data
    itineraries = Itinerary.query.filter_by(company_id=company.id).all()
    return render_template('admin/dashboard.html', 
                         itineraries=itineraries, 
                         company=company, 
                         user=user)

@app.route('/admin/itinerary/new', methods=['GET', 'POST'])
@login_required()
def new_itinerary():
    """Create new itinerary"""
    company = get_current_company()
    if not company:
        flash('No company associated with your account.', 'error')
        return redirect(url_for('logout'))
    
    if request.method == 'POST':
        itinerary = Itinerary(
            name=request.form['name'],
            description=request.form['description'],
            company_id=company.id
        )
        db.session.add(itinerary)
        db.session.commit()
        flash('Itinerary created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/new_itinerary.html', company=company)

@app.route('/admin/itinerary/<int:itinerary_id>')
@login_required()
def manage_itinerary(itinerary_id):
    """Manage specific itinerary and its stops"""
    company = get_current_company()
    if not company:
        flash('No company associated with your account.', 'error')
        return redirect(url_for('logout'))
    
    itinerary = Itinerary.query.filter_by(id=itinerary_id, company_id=company.id).first_or_404()
    stops = Stop.query.filter_by(itinerary_id=itinerary_id).order_by(Stop.day_number, Stop.order_in_day).all()
    
    # Group stops by day
    stops_by_day = {}
    for stop in stops:
        if stop.day_number not in stops_by_day:
            stops_by_day[stop.day_number] = []
        stops_by_day[stop.day_number].append(stop)
    
    return render_template('admin/manage_itinerary.html', itinerary=itinerary, stops_by_day=stops_by_day, company=company)

@app.route('/admin/stop/new/<int:itinerary_id>', methods=['GET', 'POST'])
@login_required()
def new_stop(itinerary_id):
    """Add new stop to itinerary"""
    company = get_current_company()
    if not company:
        flash('No company associated with your account.', 'error')
        return redirect(url_for('logout'))
    
    itinerary = Itinerary.query.filter_by(id=itinerary_id, company_id=company.id).first_or_404()
    
    if request.method == 'POST':
        # Handle file upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
        
        stop = Stop(
            name=request.form['name'],
            description=request.form['description'],
            latitude=float(request.form['latitude']),
            longitude=float(request.form['longitude']),
            day_number=int(request.form['day_number']),
            order_in_day=int(request.form.get('order_in_day', 1)),
            image_filename=image_filename,
            itinerary_id=itinerary_id
        )
        db.session.add(stop)
        db.session.commit()
        flash('Stop added successfully!', 'success')
        return redirect(url_for('manage_itinerary', itinerary_id=itinerary_id))
    
    return render_template('admin/new_stop.html', itinerary=itinerary)

@app.route('/admin/toggle_day/<int:itinerary_id>/<int:day_number>', methods=['POST'])
def toggle_day_activation(itinerary_id, day_number):
    """Toggle activation status for all stops in a specific day"""
    data = request.get_json()
    is_active = data.get('is_active', False)
    
    stops = Stop.query.filter_by(itinerary_id=itinerary_id, day_number=day_number).all()
    for stop in stops:
        stop.is_day_active = is_active
    
    db.session.commit()
    return jsonify({'success': True, 'message': f'Day {day_number} {"activated" if is_active else "deactivated"}'})

@app.route('/admin/stop/edit/<int:stop_id>', methods=['GET', 'POST'])
def edit_stop(stop_id):
    """Edit existing stop"""
    stop = Stop.query.get_or_404(stop_id)
    
    if request.method == 'POST':
        stop.name = request.form['name']
        stop.description = request.form['description']
        stop.latitude = float(request.form['latitude'])
        stop.longitude = float(request.form['longitude'])
        stop.day_number = int(request.form['day_number'])
        stop.order_in_day = int(request.form.get('order_in_day', 1))
        
        # Handle new image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                # Delete old image if exists
                if stop.image_filename:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], stop.image_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = secure_filename(file.filename)
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                stop.image_filename = filename
        
        db.session.commit()
        flash('Stop updated successfully!', 'success')
        return redirect(url_for('manage_itinerary', itinerary_id=stop.itinerary_id))
    
    return render_template('admin/edit_stop.html', stop=stop)

@app.route('/admin/stop/delete/<int:stop_id>', methods=['POST'])
def delete_stop(stop_id):
    """Delete a stop"""
    stop = Stop.query.get_or_404(stop_id)
    itinerary_id = stop.itinerary_id
    
    # Delete associated image file
    if stop.image_filename:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], stop.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(stop)
    db.session.commit()
    flash('Stop deleted successfully!', 'success')
    return redirect(url_for('manage_itinerary', itinerary_id=itinerary_id))

if __name__ == '__main__':
    with app.app_context():
        # Check if database exists and has data
        try:
            user_count = User.query.count()
            if user_count == 0:
                print("⚠️  No users found in database!")
                print("🔄 Please run: python init_db.py")
                print("   This will create the database and default accounts.")
                exit(1)
        except Exception as e:
            print("⚠️  Database not initialized!")
            print("🔄 Please run: python init_db.py")
            print("   This will create the database and default accounts.")
            exit(1)
        
        print("\n" + "="*60)
        print("🚀 MULTI-TENANT TOURISM PLATFORM")
        print("="*60)
        print("🌐 URLs:")
        print("   Public Site: http://127.0.0.1:5000")
        print("   Login Page: http://127.0.0.1:5000/login")
        print("   Registration: http://127.0.0.1:5000/register")
        print("   Super Admin: http://127.0.0.1:5000/super-admin")
        print("   Company Admin: http://127.0.0.1:5000/admin")
        print("\n📋 Default Login Credentials:")
        print("   Super Admin: admin@tourism.com / admin123")
        print("   Demo Company: demo@company.com / demo123")
        print("="*60)
    
    app.run(debug=True, host='127.0.0.1', port=5000)

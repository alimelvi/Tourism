#!/usr/bin/env python3
"""
Database initialization script for Tourism Platform
Creates tables and initial super admin user
"""

from app import app, db, User, Company, Itinerary, Stop
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def init_database():
    """Initialize database with tables and super admin user"""
    
    with app.app_context():
        print("🔄 Dropping existing tables...")
        db.drop_all()
        
        print("🔄 Creating new tables...")
        db.create_all()
        
        print("🔄 Creating super admin user...")
        
        # Create super admin user (no company)
        super_admin = User(
            username='admin@tourism.com',
            email='admin@tourism.com',
            password_hash=generate_password_hash('admin123'),
            first_name='Super',
            last_name='Admin',
            role='super_admin',
            company_id=None  # Super admin has no company
        )
        
        db.session.add(super_admin)
        
        # Create a demo company for testing
        demo_company = Company(
            name='Demo Tourism Company',
            email='demo@company.com',
            phone='+92-300-1234567',
            address='123 Main Street, Gulberg',
            city='Lahore',
            country='Pakistan',
            website='https://www.demotours.com',
            subscription_plan='premium',
            subscription_expires=datetime.utcnow() + timedelta(days=365)
        )
        
        db.session.add(demo_company)
        db.session.flush()  # Get company ID
        
        # Create demo company admin user
        demo_admin = User(
            username='demo@company.com',
            email='demo@company.com',
            password_hash=generate_password_hash('demo123'),
            first_name='Demo',
            last_name='Admin',
            role='admin',
            company_id=demo_company.id
        )
        
        db.session.add(demo_admin)
        
        # Create a sample itinerary
        sample_itinerary = Itinerary(
            name='Lahore Heritage Tour',
            description='Explore the historic walled city of Lahore with its magnificent Mughal architecture.',
            company_id=demo_company.id,
            is_active=True
        )
        
        db.session.add(sample_itinerary)
        db.session.flush()  # Get itinerary ID
        
        # Create sample stops
        sample_stops = [
            {
                'name': 'Badshahi Mosque',
                'description': 'One of the largest mosques in the world, built by Emperor Aurangzeb in 1673. This magnificent red sandstone mosque can accommodate 55,000 worshippers.',
                'latitude': 31.5881,
                'longitude': 74.3099,
                'day_number': 1,
                'order_in_day': 1,
                'is_day_active': True
            },
            {
                'name': 'Lahore Fort (Shahi Qila)',
                'description': 'A UNESCO World Heritage site, this massive fort contains the finest examples of Mughal architecture including the famous Sheesh Mahal (Palace of Mirrors).',
                'latitude': 31.5882,
                'longitude': 74.3142,
                'day_number': 1,
                'order_in_day': 2,
                'is_day_active': True
            },
            {
                'name': 'Wazir Khan Mosque',
                'description': 'Famous for its intricate tile work and calligraphy, this 17th-century mosque is considered one of the most ornately decorated Mughal monuments.',
                'latitude': 31.5827,
                'longitude': 74.3142,
                'day_number': 1,
                'order_in_day': 3,
                'is_day_active': True
            },
            {
                'name': 'Food Street (Gawalmandi)',
                'description': 'Experience authentic Lahori cuisine at this famous food street. Try traditional dishes like nihari, haleem, and kulfi.',
                'latitude': 31.5804,
                'longitude': 74.3087,
                'day_number': 2,
                'order_in_day': 1,
                'is_day_active': False
            },
            {
                'name': 'Anarkali Bazaar',
                'description': 'One of the oldest surviving markets in South Asia, perfect for shopping traditional handicrafts, fabrics, and souvenirs.',
                'latitude': 31.5497,
                'longitude': 74.3436,
                'day_number': 2,
                'order_in_day': 2,
                'is_day_active': False
            }
        ]
        
        for stop_data in sample_stops:
            stop = Stop(
                name=stop_data['name'],
                description=stop_data['description'],
                latitude=stop_data['latitude'],
                longitude=stop_data['longitude'],
                day_number=stop_data['day_number'],
                order_in_day=stop_data['order_in_day'],
                is_day_active=stop_data['is_day_active'],
                itinerary_id=sample_itinerary.id
            )
            db.session.add(stop)
        
        db.session.commit()
        
        print("✅ Database initialized successfully!")
        print("\n" + "="*60)
        print("🎉 SETUP COMPLETE!")
        print("="*60)
        print("📋 Login Credentials:")
        print("   Super Admin: admin@tourism.com / admin123")
        print("   Demo Company: demo@company.com / demo123")
        print("\n🌐 URLs:")
        print("   Public Site: http://127.0.0.1:5000")
        print("   Login Page: http://127.0.0.1:5000/login")
        print("   Super Admin: http://127.0.0.1:5000/super-admin")
        print("   Company Admin: http://127.0.0.1:5000/admin")
        print("="*60)

if __name__ == '__main__':
    init_database()

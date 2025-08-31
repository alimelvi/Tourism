# 🏢 Multi-Tenant Tourism Platform

A comprehensive SaaS platform for tourism companies to manage and display interactive itineraries with real road routing, designed for tourists, company administrators, and platform management.

## ✨ Features

### For Tourists (Users)
- 🗺️ **Interactive Map** with multiple view options (Street, Satellite, Terrain)
- 📍 **Clickable Stop Markers** with detailed information
- 🔊 **Text-to-Speech** functionality for stop descriptions
- 📱 **Responsive Design** that works on all devices
- 🧭 **User Location** detection and display
- 📊 **Day Progress Tracking** to see trip progression
- 🛣️ **Route Visualization** between stops

### For Company Administrators
- 📋 **Itinerary Management** - Create and manage company-specific itineraries
- 📍 **Stop Management** - Add, edit, and delete stops with images
- 📅 **Day Activation Control** - Enable/disable days as trips progress
- 🖼️ **Image Upload** for stops
- 📈 **Company Dashboard** with statistics and quick actions
- ⚡ **Real-time Updates** for day activation
- 🏢 **Company Branding** - Each company manages their own content

### For Platform Administrators (Super Admin)
- 🏢 **Company Management** - Approve, activate, and manage tourism companies
- 👥 **User Management** - Oversee all platform users
- 📊 **Platform Analytics** - System-wide statistics and usage metrics
- 🔧 **System Administration** - Platform-wide settings and maintenance
- 💰 **Subscription Management** - Handle billing and plan upgrades
- 🚀 **Multi-tenant Control** - Complete platform oversight

## 🚀 Quick Start Guide

### Step 1: Install Python
Make sure you have Python 3.7 or higher installed on your computer.
- Download Python from: https://www.python.org/downloads/
- During installation, make sure to check "Add Python to PATH"

### Step 2: Open Command Prompt
1. Press `Windows + R`
2. Type `cmd` and press Enter
3. Navigate to your Tourism folder:
   ```
   cd D:\Tourism
   ```

### Step 3: Install Required Packages
Copy and paste this command, then press Enter:
```
pip install -r requirements.txt
```

### Step 4: Initialize Database
Copy and paste this command, then press Enter:
```
python init_db.py
```

### Step 5: Run the Application
Copy and paste this command, then press Enter:
```
python app.py
```

### Step 6: Open Your Browser
1. Open your web browser (Chrome, Firefox, Edge, etc.)
2. Go to: http://127.0.0.1:5000

### Step 7: Login with Demo Accounts
- **Super Admin**: admin@tourism.com / admin123
- **Demo Company**: demo@company.com / demo123

That's it! Your multi-tenant platform is now running! 🎉

## 📱 How to Use

### For Users (Viewing Itineraries)
1. **Homepage**: Visit http://127.0.0.1:5000
2. **Select Itinerary**: Choose from the dropdown menu
3. **Explore Stops**: Click on green markers for active stops
4. **Listen to Descriptions**: Use the speaker button in popups
5. **Change Map Views**: Use the Street/Satellite/Terrain buttons

### For Company Administrators (Managing Content)
1. **Login**: Visit http://127.0.0.1:5000/login with your company credentials
2. **Admin Panel**: Access your company dashboard
3. **Create Itinerary**: Click "Create New Itinerary"
4. **Add Stops**: Click "Manage" on an itinerary, then "Add Stop"
5. **Upload Images**: Use the image upload feature when adding stops
6. **Activate Days**: Toggle the switches to activate/deactivate days

### For New Companies (Registration)
1. **Register**: Visit http://127.0.0.1:5000/register
2. **Company Info**: Fill in your tourism company details
3. **Admin Account**: Create your admin user account
4. **Free Trial**: Get 30 days free access to all features
5. **Start Creating**: Begin building your itineraries immediately

### For Platform Administrators (Super Admin)
1. **Super Admin Panel**: Visit http://127.0.0.1:5000/super-admin
2. **Manage Companies**: Approve, activate, or deactivate companies
3. **User Management**: Oversee all platform users
4. **Analytics**: View platform-wide statistics and usage
5. **System Health**: Monitor platform performance

## 📁 Project Structure

```
Tourism/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # User interface
│   └── admin/            # Admin templates
├── static/               # Static files
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── uploads/          # Uploaded images
└── tourism_app.db        # Database (created automatically)
```

## 🔧 Technical Details

- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (no setup required)
- **Maps**: Leaflet.js with OpenStreetMap
- **Styling**: Bootstrap 5

## 💡 Tips for Best Results

### Adding Stops
1. **Get Coordinates**: 
   - Go to Google Maps
   - Right-click on the exact location
   - Copy the numbers that appear (latitude, longitude)

2. **Good Descriptions**:
   - Write 2-3 sentences describing the location
   - Include historical or cultural information
   - Mention what visitors can do there
   - Keep it engaging but concise

3. **Quality Images**:
   - Use high-resolution photos
   - Make sure images are well-lit
   - Landscape orientation works best

### Managing Itineraries
1. **Day Organization**: 
   - Group nearby stops on the same day
   - Consider travel time between locations
   - Don't overcrowd days with too many stops

2. **Activation Strategy**:
   - Activate Day 1 when the trip starts
   - Activate subsequent days as the trip progresses
   - Keep future days inactive to maintain suspense

## 🛠️ Troubleshooting

### Common Issues

**Problem**: "python is not recognized"
**Solution**: Make sure Python is installed and added to PATH. Restart command prompt after installation.

**Problem**: "pip is not recognized"
**Solution**: Use `python -m pip install -r requirements.txt` instead.

**Problem**: Can't access the website
**Solution**: Make sure the app is running (you should see "Running on http://127.0.0.1:5000"). Check that you're using the correct URL.

**Problem**: Images not showing
**Solution**: Make sure image files are under 10MB and in JPG, PNG, or GIF format.

**Problem**: Coordinates not working
**Solution**: Double-check latitude (-90 to 90) and longitude (-180 to 180) values are correct.

### Getting Help
If you encounter any issues:
1. Make sure all commands were typed exactly as shown
2. Check that your internet connection is working (for map tiles)
3. Try refreshing your browser page
4. Restart the app by pressing Ctrl+C in command prompt, then running `python app.py` again

## 🔄 Stopping the Application
To stop the application:
1. Go to the command prompt window
2. Press `Ctrl + C`
3. Close the command prompt window

## 🌐 Deploying to the Web
When you're ready to deploy this app to the internet, you'll need:
- A web hosting service (like Heroku, PythonAnywhere, or DigitalOcean)
- To update the database configuration for production
- To set up environment variables for security

The current setup is perfect for local testing and development!

## 📞 Support
This app was designed to be simple and user-friendly. All the features work offline except for the map tiles, which require an internet connection.

Enjoy creating amazing tourism experiences! 🏝️✈️🗺️

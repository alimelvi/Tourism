@echo off
echo ================================================
echo      MULTI-TENANT TOURISM PLATFORM
echo ================================================
echo.
echo Installing requirements...
pip install -r requirements.txt
echo.
echo Checking database...
python -c "from app import app, db, User; import sys; app.app_context().push(); sys.exit(0 if User.query.count() > 0 else 1)" 2>nul
if errorlevel 1 (
    echo.
    echo Database not found or empty. Initializing...
    python init_db.py
    echo.
)
echo.
echo Starting the web server...
echo.
echo ================================================
echo   IMPORTANT: Keep this window open while using the app
echo ================================================
echo.
echo   🌐 URLs:
echo   Public Site:    http://127.0.0.1:5000
echo   Login:          http://127.0.0.1:5000/login
echo   Register:       http://127.0.0.1:5000/register
echo   Super Admin:    http://127.0.0.1:5000/super-admin
echo   Company Admin:  http://127.0.0.1:5000/admin
echo.
echo   📋 Default Accounts:
echo   Super Admin:    admin@tourism.com / admin123
echo   Demo Company:   demo@company.com / demo123
echo.
echo   Press Ctrl+C to stop the app when you're done
echo ================================================
echo.
python app.py
pause

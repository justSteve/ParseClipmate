@echo off
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b %errorlevel%
)

echo Running parser...
python main.py
if %errorlevel% neq 0 (
    echo Parser failed.
    pause
    exit /b %errorlevel%
)

echo Starting server...
echo Open http://localhost:8000 in your browser
python server.py

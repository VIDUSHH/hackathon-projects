@echo off
echo Starting Reckon AI (Neural Agents) Setup and Run...

echo.
echo ========================================
echo Checking Backend Requirements...
echo ========================================
cd backend
if not exist "venv" (
    echo Python virtual environment not found. Installing backend dependencies...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install fastapi uvicorn pandas prophet python-multipart python-dotenv google-generativeai
) else (
    echo Backend environment found.
)

:: Start Backend in a new window
echo Starting the Backend Server on Port 8000...
start cmd /k "title Reckon AI - Backend && call venv\Scripts\activate.bat && uvicorn app:app --reload"
cd ..

echo.
echo ========================================
echo Checking Frontend Requirements...
echo ========================================
cd frontend
if not exist "node_modules" (
    echo Node modules not found. Installing frontend dependencies...
    npm install
) else (
    echo Frontend node_modules found.
)

:: Start Frontend in a new window
echo Starting the Frontend React App...
start cmd /k "title Reckon AI - Frontend && npm run dev"
cd ..

echo.
echo ========================================
echo Both servers are starting up!
echo Keep the new command prompt windows open.
echo.
echo If this is your first time, make sure to add your GEMINI_API_KEY inside backend/.env
echo ========================================
pause

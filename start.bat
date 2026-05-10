@echo off
echo ========================================
echo   PersonaLingo v2 - Windows Launcher
echo ========================================
echo.

echo [1/2] Starting Backend (port 9849)...
cd backend
start /B cmd /c "pip install -r requirements.txt >nul 2>&1 && python run.py"
cd ..

echo [2/2] Starting Frontend (port 5273)...
cd frontend
start /B cmd /c "npm install >nul 2>&1 && npm run dev"
cd ..

echo.
echo ========================================
echo   Backend:  http://localhost:9849
echo   Frontend: http://localhost:5273
echo ========================================
echo.
echo Press Ctrl+C to stop all services.
pause

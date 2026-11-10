@echo off
title NutriPlate AI - Complete Project Launcher
color 0A
echo =====================================================================
echo           NutriPlate AI - Indian Smart Plate Assessment
echo                  Live Demonstration Launcher
echo =====================================================================
echo.

cd /d "%~dp0"

echo [*] Cleaning any previous lingering port bindings (3000 / 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do taskkill /f /pid %%a >nul 2>&1

echo [1/3] Starting FastAPI AI Neural Engine on port 8000...
start "NutriPlate AI Engine (FastAPI :8000)" cmd /k "cd ai-model && python -m uvicorn app:app --host 0.0.0.0 --port 8000"

echo [2/3] Waiting 4 seconds for AI models to initialize...
timeout /t 4 /nobreak >nul

echo [3/3] Starting Node.js Fullstack Server on port 3000...
start "NutriPlate Web Backend (:3000)" cmd /k "node backend/server.js"

echo.
echo =====================================================================
echo  NutriPlate System is LIVE!
echo  - Frontend & Backend: http://localhost:3000
echo  - AI Vision Microservice: http://localhost:8000/docs
echo =====================================================================
echo.

timeout /t 2 /nobreak >nul
start http://localhost:3000

echo Both servers launched in separate windows. Press any key to close this launcher.
pause >nul

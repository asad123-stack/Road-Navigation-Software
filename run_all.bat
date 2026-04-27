@echo off
cd /d %~dp0
start "SmartHelmet Backend" cmd /k run_backend.bat
start "SmartHelmet Frontend" cmd /k run_frontend.bat

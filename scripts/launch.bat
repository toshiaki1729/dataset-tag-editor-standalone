@echo off

cd /d %~dp0
cd ..

set PYTHON=python
set "VENV_DIR=%cd%\venv"

dir "%VENV_DIR%\Scripts\Python.exe"
if %ERRORLEVEL% == 0 goto :activate

echo "Cannot find venv folder. Please run install.bat first."
pause
exit /b

:activate
set PYTHON="%VENV_DIR%\Scripts\Python.exe"
echo venv %PYTHON%

%PYTHON% scripts\launch.py %*
pause
exit /b
@echo off
setlocal

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" goto install

where py >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_COMMAND=py -3"
) else (
    where python >nul 2>nul
    if errorlevel 1 (
        echo Python was not found. Install Python 3.12 or later and try again.
        exit /b 1
    )
    set "PYTHON_COMMAND=python"
)

%PYTHON_COMMAND% -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)"
if errorlevel 1 (
    echo Python 3.12 or later is required.
    exit /b 1
)

echo Creating virtual environment in .venv...
%PYTHON_COMMAND% -m venv ".venv"
if errorlevel 1 exit /b 1

:install
".venv\Scripts\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)"
if errorlevel 1 (
    echo The existing .venv uses Python older than 3.12.
    echo Remove .venv and run setup.bat again with a supported Python version.
    exit /b 1
)

echo Updating pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 exit /b 1

echo Installing project dependencies...
".venv\Scripts\python.exe" -m pip install -r "requirements.txt"
if errorlevel 1 exit /b 1

echo.
echo Setup complete.
echo Run the application with: .venv\Scripts\python.exe main.py

endlocal

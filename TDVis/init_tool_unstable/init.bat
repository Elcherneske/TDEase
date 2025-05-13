@echo off
chcp 65001 > nul
cd /d "%~dp0"

:: File existence check
if not exist "requirements.txt" (
    echo Error: requirements.txt not found
    pause
    exit /b 1
)

:: Python environment check
where python >nul 2>&1
if %errorlevel% neq 0 goto INSTALL_PYTHON

python -c "import sys; exit(0) if (sys.version_info >= (3,8)) else exit(1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python 3.8+ required
    echo Download from: https://www.python.org/downloads/
    echo Remember to check "Add python.exe to PATH" during installation
    pause
    exit /b 1
)

:: UV installation
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing uv...
    python -m pip install --user uv >nul 2>&1
    if %errorlevel% neq 0 (
        echo ✗ UV installation failed
        pause
        exit /b 1
    )
)

:: Virtual environment setup
if exist ".venv" rmdir /s /q .venv >nul 2>&1
uv venv .venv --python python --seed --index-url=https://pypi.tuna.tsinghua.edu.cn/simple
if %errorlevel% neq 0 (
    echo ✗ Virtual environment creation failed
    echo Possible causes:
    echo 1. .venv directory is locked
    echo 2. Network connection issues
    echo Please delete .venv manually and retry
    pause
    exit /b 1
)

:: Dependency installation
echo [1/2] Installing core dependencies...
uv pip install -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple --link-mode=copy
if %errorlevel% neq 0 (
    echo ✗ Dependency installation failed
    goto INSTALL_FAIL
)

:: Environment validation
echo [2/2] Verifying installation...
.venv\Scripts\python -c "import streamlit, pandas" >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Critical components missing: streamlit or pandas
    goto INSTALL_FAIL
)

echo ✓ Environment validation passed
goto INSTALL_SUCCESS

:INSTALL_SUCCESS
echo Starting Streamlit service...
streamlit run "%~dp0scripts\MainPage.py"
exit /b 0

:INSTALL_FAIL
echo Suggested actions:
echo 1. Check network connection
echo 2. View installation log: type %LOG_FILE%
echo 3. Try manual dependency installation
echo 4. Verify Python is in PATH
pause
exit /b 1

:INSTALL_PYTHON
echo Error: Python not detected
echo Installation steps:
echo 1. Visit https://www.python.org/downloads/
echo 2. Install Python 3.8+
echo 3. Check "Add python.exe to PATH"
echo 4. Re-run this script
pause
exit /b 1
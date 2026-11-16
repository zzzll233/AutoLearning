@echo off
setlocal

set "PROJECT_DIR=D:\ALearning\PythonProject\AUTOLearning"
set "PYTHON_EXE=.venv\Scripts\python.exe"
set "REPORT=reports\order-api.xml"

pushd "%PROJECT_DIR%" || (
    echo Cannot open project directory: "%PROJECT_DIR%"
    pause
    exit /b 1
)

if not exist "%PYTHON_EXE%" (
    echo Cannot find the virtual environment: "%CD%\%PYTHON_EXE%"
    popd
    pause
    exit /b 1
)

set "RUN_MODE="
choice /c 12 /n /m "1 = Quick check, 2 = Full regression: "
set "MENU_CHOICE=%ERRORLEVEL%"

if "%MENU_CHOICE%"=="1" set "RUN_MODE=quick"
if "%MENU_CHOICE%"=="2" set "RUN_MODE=full"

if not defined RUN_MODE (
    popd
    exit /b 2
)

"%PYTHON_EXE%" run_tests.py "%RUN_MODE%"
set "RUN_EXIT=%ERRORLEVEL%"

echo Runner exit code: %RUN_EXIT%
popd
pause
exit /b %RUN_EXIT%
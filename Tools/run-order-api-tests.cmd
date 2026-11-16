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

set "TEST_TARGET="
choice /c 12 /n /m "1 = Quick check, 2 = Full regression: "
set "MODE=%ERRORLEVEL%"

if "%MODE%"=="1" set "TEST_TARGET=test_db_order.py::test_order_api_matches_database"
if "%MODE%"=="2" set "TEST_TARGET=test_db_order.py"

if not defined TEST_TARGET (
    popd
    exit /b 2
)

echo Running order lookup tests. Flask on port 5051 and MySQL must be running.
"%PYTHON_EXE%" -m pytest -v "%TEST_TARGET%" --junitxml="%REPORT%" --html=reports/order-api.html --self-contained-html
set "TEST_EXIT=%ERRORLEVEL%"
if exist "%REPORT%" (
    "%PYTHON_EXE%" summarize_results.py "%REPORT%"
)

echo(
echo pytest exit code: %TEST_EXIT%
echo Report location: "%CD%\%REPORT%"
popd
pause
exit /b %TEST_EXIT%

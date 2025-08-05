@echo off
echo Installing MEGA Test System Dependencies...
echo ==========================================

echo.
echo Updating pip...
python -m pip install --upgrade pip

echo.
echo Installing requirements...
python -m pip install -r thesis_tests\requirements_tests.txt

echo.
echo Installing spaCy language model...
python -m spacy download en_core_web_sm

echo.
echo Creating directories...
if not exist "thesis_tests\test_data" mkdir "thesis_tests\test_data"
if not exist "thesis_tests\linkography_data" mkdir "thesis_tests\linkography_data"
if not exist "thesis_tests\uploads" mkdir "thesis_tests\uploads"
if not exist "benchmarking\data\sessions" mkdir "benchmarking\data\sessions"

echo.
echo ==========================================
echo Installation complete!
echo.
echo To run the test dashboard:
echo   python launch_test_dashboard.py
echo.
echo Note: Make sure you have a .env file with:
echo   OPENAI_API_KEY=your-api-key-here
echo.
pause
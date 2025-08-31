@echo off
echo 🧪 Starting Task Trigger Tester...
echo.
echo This app tests all 8 tasks without OpenAI API
echo.
echo Key Features:
echo - Test Task 2.1 at visualization 0%% (your main concern)
echo - Test all 8 tasks across 3 phases
echo - Phase transition testing
echo - Real-time task manager status
echo.
echo Opening in browser...
echo.

streamlit run task_trigger_tester.py --server.port 8503

pause

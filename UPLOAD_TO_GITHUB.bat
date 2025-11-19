@echo off
cls
echo ================================================
echo   UPLOAD TO GITHUB
echo ================================================
echo.
echo This will push your project to:
echo https://github.com/OmerBentzi/Automatiq_ai.git
echo.
echo Make sure you have:
echo  1. Git installed
echo  2. GitHub authentication configured
echo.
pause

echo.
echo [1/6] Initializing Git repository...
git init

echo.
echo [2/6] Adding all files...
git add .

echo.
echo [3/6] Creating first commit...
git commit -m "Initial commit: CyberSecurity Training Assistant - Full production system with AI agent, FastAPI backend, React frontend, comprehensive guardrails, and complete documentation"

echo.
echo [4/6] Adding remote repository...
git remote add origin https://github.com/OmerBentzi/Automatiq_ai.git

echo.
echo [5/6] Checking if remote exists...
git remote -v

echo.
echo [6/6] Pushing to GitHub...
echo NOTE: You may need to authenticate
echo.
git branch -M main
git push -u origin main

echo.
echo ================================================
echo   UPLOAD COMPLETE!
echo ================================================
echo.
echo Your project is now at:
echo https://github.com/OmerBentzi/Automatiq_ai
echo.
pause


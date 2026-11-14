@echo off
title Cai dat Chay Ngam Tu Dong Khi Bat May (ChemA+ Studio)
cd /d "%~dp0"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
copy /Y "%~dp0run_hidden_background.vbs" "%STARTUP_DIR%\ChemAPlus_Background_Server.vbs" >nul
cscript //nologo "%~dp0run_hidden_background.vbs"
echo ======================================================================
echo   [OK] Da cai dat ChemA+ Studio chay ngam tu dong cung Windows!
echo   Tu nay ban khong can bat cua so server thu cong nua.
echo ======================================================================
pause

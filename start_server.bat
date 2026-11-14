@echo off
title DUMTP ChemA+ Studio Server
cd /d "%~dp0"
echo ======================================================================
echo   STARTING DUMTP CHEMA+ STUDIO SERVER (PORT 8080)
echo ======================================================================
where cargo >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [+] Rust Cargo found! Launching Axum server...
    start "" "http://localhost:8080"
    cargo run --release
    goto :eof
)
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [+] Python found! Launching local server on http://localhost:8080 ...
    start "" "http://localhost:8080"
    python server.py
    goto :eof
)
echo [!] Opening public\index.html directly in browser...
start "" "%~dp0public\index.html"

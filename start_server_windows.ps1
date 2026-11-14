# DUMTP ChemA+ Studio - Windows Server Launcher (Pure ASCII for PowerShell 5.1+ Compatibility)
$ErrorActionPreference = "Continue"
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  DUMTP CHEMA+ STUDIO SERVER (RUST AXUM + C++17 + SQLITE + E2EE)" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

if (Get-Command g++ -ErrorAction SilentlyContinue) {
    Write-Host "[+] Compiling C++17 Graphics Engine (chem_gfx_engine.cpp)..." -ForegroundColor Yellow
    g++ -O3 -std=c++17 cpp_graphics/chem_gfx_engine.cpp -o cpp_graphics/chem_gfx_engine.exe
}

if (Get-Command cargo -ErrorAction SilentlyContinue) {
    Write-Host "[+] Rust Cargo detected! Starting Axum + Askama/Tera server on port 8080..." -ForegroundColor Green
    Start-Process "http://localhost:8080"
    cargo run --release
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "[+] Starting local web server on http://localhost:8080 ..." -ForegroundColor Green
    Start-Process "http://localhost:8080"
    python server.py
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    Write-Host "[+] Starting local web server on http://localhost:8080 ..." -ForegroundColor Green
    Start-Process "http://localhost:8080"
    python3 server.py
} else {
    Write-Host "[!] Opening public/index.html directly in your browser..." -ForegroundColor Yellow
    Start-Process (Join-Path $scriptDir "public\index.html")
}

@echo off
setlocal
cd /d %~dp0
powershell -ExecutionPolicy Bypass -File bootstrap\bootstrap_windows.ps1
endlocal

@echo off
REM Build OGX-Mini for Pico 2 W (uses VS for pioasm/picotool). Run from RP2040 folder.
cd /d "%~dp0.."
powershell -ExecutionPolicy Bypass -File "%~dp0build-with-vs.ps1" %*
exit /b %ERRORLEVEL%

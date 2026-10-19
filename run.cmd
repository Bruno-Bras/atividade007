@echo off
REM Roda a Atividade 007. Ex.: run.cmd  |  run.cmd -Reset  |  run.cmd -Test
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1" %*
pause

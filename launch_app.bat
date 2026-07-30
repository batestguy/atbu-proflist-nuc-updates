@echo off
REM ATBU Academic Planning Portal Launcher
REM Uses %~dp0 to reference this batch file's directory (portable)
echo Starting ATBU Academic Planning Portal...
start "" "%~dp0dist\ATBU_Academic_Planning_Portal.exe"
exit

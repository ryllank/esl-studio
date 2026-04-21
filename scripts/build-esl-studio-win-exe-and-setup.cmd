@echo off
REM -- Build the ESL-Studio Windows executable (with PyInstaller) and the setup executable (with NSIS)

setlocal
set script_dir=%~dp0
set project_dir=%script_dir%..

set exe_script=build-esl-studio-win-exe.cmd
set setup_script=build-esl-studio-win-setup.cmd

echo -- Run the exe script.
call %script_dir%%exe_script%
set retcode=%ERRORLEVEL%
if %retcode% NEQ 0 echo Failed to build the Windows executable with PyInstaller - retcode=%retcode%
if %retcode% NEQ 0 goto :skip_to_end

echo -- Run the setup script.
call %script_dir%%setup_script%
set retcode=%ERRORLEVEL%
if %retcode% NEQ 0 echo Failed to build the Windows setup executable with NSIS - retcode=%retcode%
if %retcode% NEQ 0 goto :skip_to_end

:skip_to_end
if %retcode% NEQ 0 exit /b %retcode%


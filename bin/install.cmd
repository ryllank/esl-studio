@echo off
REM -- install.cmd - install ESL-Studio Python packages.

setlocal

set _version={version}
::echo -- _version=%_version%

set _thisDir=%~dp0

set _PYTHON=python3
%_PYTHON% -h > nul 2> nul
if %errorlevel% EQU 0 goto :got_python
set _PYTHON=python
%_PYTHON% -h > nul 2> nul
if %errorlevel% EQU 0 goto :got_python
	echo *** Error: Cannot find python3 or python command
	set retcode=2
	goto :skip_to_end
:got_python
::echo -- _PYTHON=%_PYTHON%

%_PYTHON% -c "import sys; err = 22 if sys.version_info[0] != 3 or sys.version_info[1] < 10 else 0; sys.exit(err)"
if %errorlevel% EQU 0 goto :checked_version
	for /F "delims=" %%V in ('%_PYTHON% --version') do set _pyver=%%V
	echo _pyver=%_pyver%
	echo *** Error: %_PYTHON% must be 3.10 or above (%_pyver%)
	set retcode=2
	goto :skip_to_end
:checked_version

set _PIP=pipX
%_PIP% -h > nul 2> nul
if errorlevel 1 set _PIP=%_PYTHON% -m pip
::echo -- _PIP=%_PIP%

REM -- Check if the whls are on the current directory
set _got_whls=FALSE
if exist esl_studio-%_version%-py3-none-any.whl if exist esl_diagram-%_version%-py3-none-any.whl set _got_whls=TRUE
if %_got_whls%==FALSE (
	echo *** Error: Cannot find the esl_studio and esl_diagram wheel files on this current directory
	set retcode=2
	goto :skip_to_end
)

REM -- Check if there are currently esl-studio/esl-diagram installed packages - if so uninstall them
%_PIP% show esl-studio > nul 2> nul
if %errorlevel% NEQ 0 goto :uninstalled_esl_studio
	echo Uninstalling previous esl-studio package
	%_PIP% uninstall esl-studio
:uninstalled_esl_studio
%_PIP% show esl-diagram > nul 2> nul
if %errorlevel% NEQ 0 goto :uninstalled_esl_diagram
	echo Uninstalling previous esl-diagram package
	%_PIP% uninstall esl-diagram
:uninstalled_esl_diagram

REM -- Main installation
%_PIP% install -f ./ esl_studio-%_version%-py3-none-any.whl
set retcode=%ERRORLEVEL%
if %retcode% NEQ 0 (
	echo *** Error: Problem installing ESL-Studio Python packages or dependencies - error code  %retcode%
	echo Check error messages from installation.
	echo Support is available via e-mail by way of the ESL Software website - www.isimsimulation.com
	goto :skip_to_end
)

REM -- Make esl-studio launch command
echo @echo off > .\bin\esl-studio.cmd
echo %_PYTHON% %_thisDir%bin\esl-studio.pyw %* >> .\bin\esl-studio.cmd

if defined VIRTUAL_ENV (
    echo Note: Running in a virtual environment ^(venv^) - you may run ESL-Studio in the active venv's terminal
)

:skip_to_end
if %retcode% NEQ 0 exit /b %retcode%

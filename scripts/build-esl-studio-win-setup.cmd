@echo off
REM -- Build the ESL-Studio Windows setup executable with NSIS - into /dist_setup directory

setlocal
set script_dir=%~dp0
set project_dir=%script_dir%..

echo -- Look for NSIS installation - on \Program Files (x86)\NSIS.
set _NSIS=%ProgramFiles(x86)%\NSIS\makensis.exe
if exist "%_NSIS%" goto :end_nsis_exist
	echo -- NSIS not available - can't find %_NSIS%.
	set _NSIS=
	set retcode=2
	goto :skip_to_end
:end_nsis_exist

echo -- Get the version from file.
for /f "tokens=* delims=" %%A in ('%script_dir%print-esl-studio-file-version-command.cmd') do (
    set version=%%A
)
set retcode=%ERRORLEVEL%
if %retcode% NEQ 0 echo Failed to get version from file - retcode=%retcode%
if %retcode% NEQ 0 goto :skip_to_end

set exe_name=esl_studio-%version%

set dist_exe_dir=%project_dir%\dist_exe
if not exist %dist_exe_dir%\%exe_name%.exe (
    echo -- Executable file %dist_exe_dir%\%exe_name%.exe not found.
    set retcode=2
    goto :skip_to_end
)
if exist %dist_exe_dir%\esl_studio.exe del %dist_exe_dir%\esl_studio.exe
copy %dist_exe_dir%\%exe_name%.exe %dist_exe_dir%\esl_studio.exe

set dist_setup_dir=%project_dir%\dist_setup
set build_setup_dir=%project_dir%\build_setup

if not exist %dist_setup_dir% mkdir %dist_setup_dir%
if exist %build_setup_dir% rmdir /s /q %build_setup_dir%

mkdir %build_setup_dir%\bin
mkdir %build_setup_dir%\docs
mkdir %build_setup_dir%\examples

copy %dist_exe_dir%\esl_studio.exe %build_setup_dir%\bin\esl_studio.exe
copy %project_dir%\docs\install\readme.txt %build_setup_dir%\docs\readme.txt
copy %project_dir%\docs\install\licence.txt %build_setup_dir%\docs\licence.txt
copy %project_dir%\examples\*.eslstudio %build_setup_dir%\examples

echo -- Get/set envars PRODUCT_VERSION_ALL PRODUCT_VERSION and PRODUCT_BUILD_TIME from python esl_studio package
REM -- Note ESL-Studio NSIS script requires plain 4 element PRODUCT_VERSION envvar.

pushd  %project_dir%\packages\esl_studio\src
for /F %%V in ('python -c "import esl_studio; print(esl_studio.version)"') do set PRODUCT_VERSION_ALL=%%V
if errorlevel 1 goto :skip_to_end
if not "%PRODUCT_VERSION_ALL:.post=%" == "%PRODUCT_VERSION_ALL%" goto :set_version_4_elements
	set PRODUCT_VERSION=%PRODUCT_VERSION_ALL%
	goto :end_set_version
:set_version_4_elements
	for /F %%V in ('python -c "import esl_studio; print(esl_studio.version[0:esl_studio.version.find(\".post\")])"') do set PRODUCT_VERSION=%%V
	if errorlevel 1 goto :skip_to_end
:end_set_version
for /F "delims=" %%T in ('python -c "import esl_studio; print(esl_studio.build_time)"') do set PRODUCT_BUILD_TIME=%%T
if errorlevel 1 goto :skip_to_end
REM -- Just want date part of PRODUCT_BUILD_TIME
set PRODUCT_BUILD_DATE=%PRODUCT_BUILD_TIME:~0,10%
REM -- Also need PRODUCT_VERSION_MAJOR and PRODUCT_VERSION_MINOR
for /F %%V in ('python -c "import esl_studio; v=esl_studio.version.split(\".\");print(str(v[0]))"') do set PRODUCT_VERSION_MAJOR=%%V
for /F %%W in ('python -c "import esl_studio; v=esl_studio.version.split(\".\");print(str(v[1]))"') do set PRODUCT_VERSION_MINOR=%%W

echo -- PRODUCT_VERSION_ALL=%PRODUCT_VERSION_ALL% PRODUCT_VERSION=%PRODUCT_VERSION%
echo -- PRODUCT_BUILD_TIME=%PRODUCT_BUILD_TIME% PRODUCT_BUILD_DATE=%PRODUCT_BUILD_DATE%
echo -- PRODUCT_VERSION_MAJOR=%PRODUCT_VERSION_MAJOR% PRODUCT_VERSION_MINOR=%PRODUCT_VERSION_MINOR%

echo -- Update the readme doc with the version and build time.
python %script_dir%build-esl-studio-utils.py substitute_in_file "%build_setup_dir%\docs\readme.txt" "{version:%PRODUCT_VERSION_ALL%,build_date:%PRODUCT_BUILD_DATE%}"
set retcode=%ERRORLEVEL%
if %retcode% NEQ 0 goto :skip_to_end

if "%_NSIS%" == "" goto :end_nsis
	echo -- Make NSIS installer.
	set installer_dir=%project_dir%\installer_nsis
	set _SRC=%build_setup_dir%
	pushd %installer_dir%
	set _target=%dist_setup_dir%\ESL-Studio.exe
	"%_NSIS%" ESLStudio.nsi
	if errorlevel 1 goto :skip_to_end
	popd
:end_nsis

REM -- Adorn the setup exe file with version and build-time
if exist %dist_setup_dir%\ESL-Studio-%PRODUCT_VERSION_ALL%-%PRODUCT_BUILD_DATE%.exe del %dist_setup_dir%\ESL-Studio-%PRODUCT_VERSION_ALL%-%PRODUCT_BUILD_DATE%.exe
rename %dist_setup_dir%\ESL-Studio.exe ESL-Studio-%PRODUCT_VERSION_ALL%-%PRODUCT_BUILD_DATE%.exe

REM -- Tidy up (we leave dist_exe_dir as we found it)
if exist %build_setup_dir% rmdir /s /q %build_setup_dir%
if exist %dist_exe_dir%\esl_studio.exe del %dist_exe_dir%\esl_studio.exe

:skip_to_end
if %retcode% NEQ 0 exit /b %retcode%


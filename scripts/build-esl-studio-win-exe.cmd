@echo off
REM -- Build the ESL-Studio Windows executable with PyInstaller - into \dist_exe directory

setlocal
set script_dir=%~dp0
set project_dir=%script_dir%..

echo -- Check have Python packages, at adequate version level, installed.
pip install setuptools setuptools_scm "wxPython>=4.2.0" PyInstaller six
::: With wxPython previously installed got (Win10/Python 3.13.5 on 2026-02-09)
::: Successfully installed PyInstaller-6.18.0 altgraph-0.17.5 packaging-26.0 pefile-2024.8.26 pyinstaller-hooks-contrib-2026.0 pywin32-ctypes-0.2.3 setuptools-82.0.0 setuptools_scm-9.2.2
set retcode=%ERRORLEVEL%
if %retcode% NEQ 0 goto :skip_to_end

set build_exe_dir=%project_dir%\build_exe
set dist_exe_dir=%project_dir%\dist_exe

if exist %build_exe_dir% rmdir /s /q %build_exe_dir%

set PYTHONPATH=%project_dir%\packages\esl_diagram\src;%project_dir%\packages\esl_studio\src

pushd %project_dir%\packages\esl_studio\src

echo -- Update the _version.py file with setuptools_scm.
echo *** need a git project to update version
python %script_dir%build-esl-studio-utils.py update_esl_studio_version_file
set retcode=%ERRORLEVEL%
REM -- update_version_file returns retcode 99 for git command not found
if %retcode% NEQ 0 if %retcode% NEQ 99 goto :skip_to_end

echo -- Get the version from file.
if not exist esl_studio\_version.py (
	echo -- Version file esl_studio\_version.py not found.
	set retcode=2
	goto :skip_to_end
)

for /f "tokens=* delims=" %%A in ('%script_dir%print-esl-studio-file-version-command.cmd') do (
    set version=%%A
)

echo -- Set the _file_version_info.txt with version  %version% (and other) info.
python %script_dir%build-esl-studio-utils.py set_esl_studio_file_version_info
set retcode=%ERRORLEVEL%
if %retcode% NEQ 0 goto :skip_to_end

echo -- Build executable with PyInstaller.
set exe_name=esl_studio-%version%
if "%1"=="no-version" set exe_name=esl_studio
REM -- --splash esl_studio\resources\splash.png ^ -- didnt work - wanted tkinter but pip couldnt find it
pyinstaller --clean --name="%exe_name%" ^
--add-data "esl_studio\profile;profile" ^
--add-data "esl_studio\resources;resources" ^
--onefile --windowed ^
--icon=esl_studio\resources\esl-studio.ico ^
--version-file %build_exe_dir%\_file_version_info.txt ^
--distpath=%dist_exe_dir% --workpath=%build_exe_dir% esl_studio\app\app.py
set retcode=%ERRORLEVEL%
popd
if %retcode% NEQ 0 goto :skip_to_end

if exist %build_exe_dir% rmdir /s /q %build_exe_dir%
if exist %project_dir%\packages\esl_studio\src\%exe_name%.spec del %project_dir%\packages\esl_studio\src\%exe_name%.spec

:skip_to_end
if %retcode% NEQ 0 exit /b %retcode%


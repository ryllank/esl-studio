@echo off
REM -- Run esl-studio Python #code directly.
setlocal

set script_dir=%~dp0
set script_drive=%~d0
set project_dir=%script_dir%..

%script_drive%
cd %script_dir%
set PYTHONPATH=%project_dir%\packages\esl_diagram\src;%project_dir%\packages\esl_studio\src
python -c "import esl_studio.app; esl_studio.app.main()" %*


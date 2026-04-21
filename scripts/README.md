ESL-Studio development scripts
==============================

Build scripts
-------------

These scripts are for building different types of distributions from the
source code:

-	`build-esl-studio-python-packages-and-archive.sh`<br>
	a Linux script to build the ESL-Studio Python packages (esl_diagram
	& esl_studio) into their own package `/package/esl_diagram|studio/dist` directories.
	Also package up in one .zip archive (with install scripts) a put
	that in a top level directory `/dist`.
-	`build-esl-studio-win-exe-and-setup.cmd`<br>
	a Windows batch script to build the ESL-Studio Windows executable
	(with PyInstaller) and the installation setup executable (with
	NSIS). It puts the plain executable in a top level directory
	`/dist_exe` and the installation setup executable in a top level
	directory `/dist_setup`.
-	`build-esl-studio-webpages.sh`<br>
	a Linux script to build the ESL-Studio webpages (using mkdocs) and
	put all the files in a top level directory `/dist_webpages`, all in
	a subdirectory `esl-studio`. This subdirectory is available to be
	deployed to a web-server. The script also produces a .zip
	archive of that subdirectory located in the `/dist_webpages`
	directory.

These scripts should work in Python virtual environments (venvs), where
applicable.

They should be able to be used in git workspace where they can get an
up-to-date project version using get_version from Python package
setuptools_scm.


Run scripts
-----------

Normally you would install ESL-Studio (from the installation setup
executable for Windows or from the installation .zip archive for Linux
(also available for Windows).

But the Python code may be run directly (for example during development)
from the project with the scripts:

-	`run-esl-studio.sh` for Linux
-	`run-esl-studio.cmd` for Windows


Ancillary scripts
-----------------

-	`build-esl-studio-python-packages.sh`<br>
	used in `build-esl-studio-python-packages-and-archive.sh`
-	`build-esl-studio-python-archive.sh`<br>
	used in `build-esl-studio-python-packages-and-archive.sh`
-	`build-esl-studio-win-exe.cmd`<br>
	used in `build-esl-studio-win-exe-and-setup.cmd`
-	`build-esl-studio-win-setup.cmd`<br>
	used in `build-esl-studio-win-exe-and-setup.cmd`
-	`build-esl-studio-utils.py`<br>
	set of Python utility functions for use in the build scripts
-	`print-scm-version-command.cmd`<br>
	Linux or Windows script using Python to print the project version
	obtained from the git workspace/repo.
-	`print-esl-studio-file-version-command.cmd`<br>
	Linux or Windows script using Python to print the project version
	obtained from the esl_package _version.py file which gets updates
	when a build is done (in a git workspace/repo).

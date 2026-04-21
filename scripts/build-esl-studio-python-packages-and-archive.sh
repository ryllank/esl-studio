#!/bin/sh
# -- Build the ESL-Studio Python packages (esl_diagram & esl_studio)
# -- into their own /dist directories.
# -- Also package up as .zip archive.

script_dir=`dirname "$0"`
project_dir=`realpath ${script_dir}/..`

packages_script=build-esl-studio-python-packages.sh
archive_script=build-esl-studio-python-archive.sh

echo -- Run the packages script.
${script_dir}/${packages_script}
retcode=$?
if [ $retcode -ne 0 ]; then
	echo -- Failed to build the python packages - retcode=$retcode
	exit $retcode
fi

if [ $retcode -eq 0 ]; then
	echo -- Run the archive script.
	${script_dir}/${archive_script}
	retcode=$?
	if [ $retcode -ne 0 ]; then
		echo -- Failed to make archive of packages - retcode=$retcode
		exit $retcode
	fi
fi
exit $retcode

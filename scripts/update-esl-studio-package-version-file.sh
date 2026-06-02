#!/bin/sh
# -- Update the esl_studio package version file.

script_dir=`dirname "$0"`
project_dir=`realpath ${script_dir}/..`

pip install setuptools setuptools_scm

python ${project_dir}/scripts/build-esl-studio-utils.py update_esl_studio_version_file
retcode=$?

if [ $retcode -ne 0 ]; then
	echo -- Failed to update the esl_studio package version file - retcode=$retcode
fi

exit $retcode

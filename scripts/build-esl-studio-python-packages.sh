#!/bin/sh
# -- Build the ESL-Studio Python packages (esl_diagram & esl_studio)
# -- into their own /dist directories.

script_dir=`dirname "$0"`
project_dir=`realpath ${script_dir}/..`

echo -- Check have the Python build package.
pip install build

echo -- Build the ESL-Diagram Python package wheel.
pushd ${project_dir}/packages/esl_diagram
python3 -m build --wheel
retcode=$?
popd

echo -- Build retcode=$retcode.
if [ $retcode -eq 0 ]; then
	if [ -d ${project_dir}/packages/esl_diagram/src/esl_diagram.egg-info ]; then
		rm -fr ${project_dir}/packages/esl_diagram/src/esl_diagram.egg-info
	fi
	if [ -d ${project_dir}/packages/esl_diagram/build ]; then
		rm -fr ${project_dir}/packages/esl_diagram/build
	fi
else
	exit $retcode
fi

echo -- Build the ESL-Studio Python package wheel.
pushd ${project_dir}/packages/esl_studio
python3 -m build --wheel
retcode=$?
popd

echo -- Build retcode=$retcode.
if [ $retcode -eq 0 ]; then
	if [ -d ${project_dir}/packages/esl_studio/src/esl_studio.egg-info ]; then
		rm -fr ${project_dir}/packages/esl_studio/src/esl_studio.egg-info
	fi
	if [ -d ${project_dir}/packages/esl_studio/build ]; then
		rm -fr ${project_dir}/packages/esl_studio/build
	fi
fi
exit $retcode

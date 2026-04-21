#!/bin/sh
# -- Build the ESL-Studio Python .zip archive into top level dist directory.

script_dir=`dirname "$0"`
project_dir=`realpath ${script_dir}/..`

echo -- Get version and build time and date from python esl_studio package.
pushd ${project_dir}/packages/esl_studio/src
version=`python -c "import esl_studio; print(esl_studio.version)"`
retcode=$?
if [ $retcode -eq 0 ]; then
	build_time=`python -c "import esl_studio; print(esl_studio.build_time)"`
	retcode=$?
fi
popd
if [ $retcode -ne 0 ]; then
	echo -- Failed to get project version and build_time via Python - retcode=$retcode.
	exit $retcod
fi
build_date=${build_time:0:10}
if [ ! -e ${project_dir}/packages/esl_diagram/dist/esl_diagram-${version}-py3-none-any.whl -o \
	 ! -e ${project_dir}/packages/esl_studio/dist/esl_studio-${version}-py3-none-any.whl ]; then
	echo -- Need both esl_diagram and esl_studio package wheels for project version $version.
	retcode=2
	exit $retcode
fi
if [ ! -d ${project_dir}/dist ]; then
	mkdir -p ${project_dir}/dist
fi

if [ -d ${project_dir}/build_zip ]; then
	rm -r -f ${project_dir}/build_zip
fi
subdir=esl-studio
mkdir -p ${project_dir}/build_zip/${subdir}
mkdir -p ${project_dir}/build_zip/${subdir}/bin
mkdir -p ${project_dir}/build_zip/${subdir}/docs
mkdir -p ${project_dir}/build_zip/${subdir}/examples

cp -p ${project_dir}/packages/esl_diagram/dist/esl_diagram-${version}-py3-none-any.whl ${project_dir}/build_zip/${subdir}/
cp -p ${project_dir}/packages/esl_studio/dist/esl_studio-${version}-py3-none-any.whl ${project_dir}/build_zip/${subdir}/
cp -p ${project_dir}/bin/install.sh ${project_dir}/build_zip/${subdir}/install.sh
cp -p ${project_dir}/bin/install.cmd ${project_dir}/build_zip/${subdir}/install.cmd
cp -p ${project_dir}/bin/esl-studio.pyw ${project_dir}/build_zip/${subdir}/bin/
cp -p ${project_dir}/bin/ESL-Studio.desktop ${project_dir}/build_zip/${subdir}/bin/
cp -p ${project_dir}/packages/esl_studio/src/esl_studio/resources/esl-studio.png ${project_dir}/build_zip/${subdir}/bin/
cp -p ${project_dir}/docs/install/readme.txt ${project_dir}/build_zip/${subdir}/docs/readme.txt
cp -p ${project_dir}/docs/install/licence.txt ${project_dir}/build_zip/${subdir}/docs/licence.txt
cp -p ${project_dir}/examples/*.eslstudio ${project_dir}/build_zip/${subdir}/examples

echo -- Update the readme doc with the version and build date.
python ${script_dir}/build-esl-studio-utils.py substitute_in_file "${project_dir}/build_zip/${subdir}/docs/readme.txt" "{version:${version},build_date:${build_date}}"
retcode=$?
if [ $retcode -ne 0 ]; then
	echo -- Failed substitution \"{version:${version},build_time:${build_time}}\" in readme file - retcode=$retcode.
	exit $retcod
fi

echo -- Update the install.sh and .cmd with the version and build date.
python ${script_dir}/build-esl-studio-utils.py substitute_in_file "${project_dir}/build_zip/${subdir}/install.sh" "{version:${version},build_date:${build_date}}"
retcode=$?
if [ $retcode -ne 0 ]; then
	echo -- Failed substitution \"{version:${version},build_time:${build_time}}\" in install.sh file - retcode=$retcode.
	exit $retcode
fi
python ${script_dir}/build-esl-studio-utils.py substitute_in_file "${project_dir}/build_zip/${subdir}/install.cmd" "{version:${version},build_date:${build_date}}"
retcode=$?
if [ $retcode -ne 0 ]; then
	echo -- Failed substitution \"{version:${version},build_time:${build_time}}\" in install.cmd file - retcode=$retcode.
	exit $retcode
fi

echo -- Make the ESL-Studio-python.zip.
target=${project_dir}/dist/ESL-Studio-python-${version}-${build_date}.zip

pushd ${project_dir}/build_zip
zip -r $target $subdir
retcode=$?
popd

if [ $retcode -eq 0 ]; then
	if [ -d ${project_dir}/build_zip ]; then
		rm -r -f ${project_dir}/build_zip
	fi
fi
exit $retcode

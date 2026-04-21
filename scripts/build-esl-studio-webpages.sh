#!/bin/sh
# -- Build the ESL-Studio webpages (using mkdocs) and put all the files
# -- in a top level directory /dist_webpages, all in a subdirectory esl-studio.
# -- Also package up the webpages as .zip archive.

script_dir=`dirname "$0"`
project_dir=`realpath ${script_dir}/..`

echo -- Check have the Python mkdocs package.
pip install mkdocs

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

dist_webpages_dir=${project_dir}/dist_webpages
subdir=esl-studio
if [ ! -d ${dist_webpages_dir} ]; then
	mkdir -p ${dist_webpages_dir}
fi
if [ -e ${dist_webpages_dir}/${subdir} ]; then
	rm -r -f ${dist_webpages_dir}/${subdir}
fi

echo -- Do mkdocs build to make the webpages.
pushd ${project_dir}/docs
mkdocs build
retcode=$?
popd
if [ $retcode -ne 0 ]; then
	echo -- Failed to build the webpages with mkdocs - retcode=$retcode.
	exit $retcod
fi
if [ ! -d ${dist_webpages_dir}/${subdir} ]; then
	echo -- Webpages ${subdir} directory not found
	exit 2
fi

echo -- Update the webpages index.html with the version and build date.
python ${script_dir}/build-esl-studio-utils.py substitute_in_file "${dist_webpages_dir}/${subdir}/index.html" "{version:${version},build_date:${build_date}}"
retcode=$?
if [ $retcode -ne 0 ]; then
	echo -- Failed substitution \"{version:${version},build_date:${build_date}}\" in readme file - retcode=$retcode.
	exit $retcod
fi

echo -- Make the ESL-Studio-webpages.zip.
target=${dist_webpages_dir}/ESL-Studio-webpages-${version}-${build_date}.zip

pushd ${dist_webpages_dir}
zip -r $target $subdir
retcode=$?
popd

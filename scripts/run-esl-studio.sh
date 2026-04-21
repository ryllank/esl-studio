#!/bin/sh
## -- Run esl-studio Python code directly.

script_dir=`dirname "$0"`
project_dir=`realpath $script_dir/..`

cd $script_dir
export PYTHONPATH="$project_dir/packages/esl_diagram/src:$project_dir/packages/esl_studio/src"
python -c "import esl_studio.app; esl_studio.app.main()" "$@"


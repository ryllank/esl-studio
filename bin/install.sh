#!/bin/bash
# -- install.sh - install ESL-Studio Python packages.

_version={version}

_thisDir=`dirname "$0"`
which realpath > /dev/null 2>&1
if [ $? -eq 0 ]
then
    _thisDir=`realpath $_thisDir`
else
    which readlink > /dev/null 2>&1
    if [ $? -eq 0 ]
    then
        _thisDir=`readlink -f $_thisDir`
    else
        echo "*** Error: Cannot determine real path of installation (need realpath or readlink)"
        exit  2 #No such file or directory
    fi
fi

# -- Check python command >= 3.10
_PYTHON=python3
which $_PYTHON > /dev/null 2>&1
if [ $? -ne 0 ]; then
    _PYTHON=python
    which $_PYTHON > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "*** Error: Cannot find python3 or python command"
        exit 2 #No such file or directory
    fi
fi
$_PYTHON -c 'import sys; err = 22 if sys.version_info[0] != 3 or sys.version_info[1] < 10 else 0; sys.exit(err)'
if [ $? -ne 0 ]; then
    _pyver=`$_PYTHON --version`
    echo "*** Error: $_PYTHON must be 3.10 or above ($_pyver)"
    exit 2 #No such file or directory
fi

# -- Check pip command module for this python
_PIP=pip
which $_PIP > /dev/null 2>&1
if [ $? -ne 0 ]; then
    _PIP="$_PYTHON -m pip"
fi
$_PIP --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "*** Error: Cannot find pip command module for $_PYTHON"
    exit 2 #No such file or directory
fi

# -- See if wxPython 4.2.0 or above is installed
_wxPython=
$_PIP show wxPython > /dev/null 2>&1
if [ $? -eq 0 ]; then
    $_PYTHON -c 'import wx; import sys; ver=list(map(lambda item: int(item), wx.__version__.split("."))); err = 0 if ver[0]>4 or (ver[0]==4 and ((ver[1]==1 and ver[2]>=1) or ver[1]>=2)) else 22; sys.exit(err)'
    if [ $? -eq 0 ]; then
        _wxPython=installed
    fi
fi

# -- Say if wxPython not installed
if [ -z "$_wxPython" ]; then
    echo wxPython 4.2.0 or above is not installed for $_PYTHON.
    echo We recommend you break here and install it before re-invoking this install script.
    echo
    echo For information on the installation see https://wxpython.org/pages/downloads/.
    echo You should ensure you have the necessary packages for your platform installed on your computer
    echo particularly if building wxPython from source.
    echo Refer also to https://wxpython.org/blog/2017-08-17-builds-for-linux-with-pip/index.html.
    echo E.g. For Ubuntu 20.04 you may need to run sudo apt install libgtk-3-dev and sudo apt install python3-pip.
    echo
    echo If you continue here the script will try to use pip to install wxPython directly.
    echo -n Do you want to continue right away? [y/N]
    read _response
    if [ "${_response:0:1}" != "y" ]; then
        exit
    fi
fi

# -- Say if will install for this user or all users - unless in a virtual environment
_idu=`id -u`
if [ -z "$VIRTUAL_ENV" ]; then
    if [ $_idu -ne 0 ]
    then
        echo Installation will be for this current user - not invoked with superuser privileges
    else
        echo Installation will be for all users - invoked with superuser privileges
    fi
    echo -n Do you want to continue installation? [y/N]
    read _response
    if [ "${_response:0:1}" != "y" ]; then
        exit 125 #Operation canceled
    fi
fi

# -- Check if the whls are on the current directory
if [ ! -e esl_studio-${_version}-py3-none-any.whl -o ! -e esl_diagram-${_version}-py3-none-any.whl ]; then
    echo "*** Error: Cannot find the esl_studio and esl_diagram wheel files on this current directory"
    exit 2 #No such file or directory
fi

# -- Check if there are currently esl-studio/esl-diagram installed packages - if so uninstall them
$_PIP show esl-studio > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo Uninstalling previous esl-studio package
    $_PIP uninstall esl-studio
fi
$_PIP show esl-diagram > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo Uninstalling previous esl-diagram package
    $_PIP uninstall esl-diagram
fi

# -- Main installation
$_PIP install -f ./ esl_studio-${_version}-py3-none-any.whl
_err=$?
if [ $_err -ne 0 ]; then
    echo "*** Error: Problem installing ESL-Studio Python packages or dependencies - error code $_err"
    echo Check error messages from installation.
    echo Support is available via e-mail by way of the ESL Software website - www.isimsimulation.com
    exit $_err
fi

# -- Make esl-studio launch command
echo "#!/usr/bin/sh" > ./bin/esl-studio
echo "$_PYTHON $_thisDir/bin/esl-studio.pyw \$*" >> ./bin/esl-studio
chmod a+x ./bin/esl-studio

# -- Edit a .desktop file with installation path (unless already there)
grep -q "Exec=$_thisDir/bin/esl-studio" ./bin/ESL-Studio.desktop
if [ $? -ne 0 ]; then
    echo Icon=$_thisDir/bin/esl-studio.png >> ./bin/ESL-Studio.desktop
    echo Exec=$_thisDir/bin/esl-studio %f >> ./bin/ESL-Studio.desktop
fi

# -- See if can, should, want to set a desktop applications menu entry (and icon for non-super user)
which xdg-desktop-menu > /dev/null 2>&1
if [ $? -eq 0 ]; then
    if [ -z "$VIRTUAL_ENV" ]; then
        if [ $_idu -eq 0 ]; then
            echo -n Do you want to setup a desktop applications menu entry? [y/N]
        else
            echo -n Do you want to setup a desktop applications menu entry and short-cut icon for this user? [y/N]
        fi
        read _response
        if [ "${_response:0:1}" == "y" ]; then
            xdg-desktop-menu install ./bin/ESL-Studio.desktop
            if [ $_idu -ne 0 ]; then
                xdg-desktop-icon install ./bin/ESL-Studio.desktop
            fi
        fi
    fi
fi

if [ -n "$VIRTUAL_ENV" ]; then
    echo "Note: Running in a virtual environment (venv) - you may run ESL-Studio in the active venv's terminal"
fi

ESL-Studio
==========

Version: {version}
Build date: {build_date}


This product, ESL-Studio, is an integrated development environment used
primarily for creating ESL simulations using block diagrams and ESL
source code. It is intended to be used with the main ESL Software
simulation product (either ESL-Pro or ESL-Lite).

On Windows, an ESL-Studio Windows executable may be included as part of
an installation of ESL.

This ESL-Studio Windows executable may be installed via its own
installation setup executable, either to update it in the ESL
installation or as its own standalone (solo) installation.

This installation setup executable may be named
`ESL-Studio-{version}-{build_date}.exe` or similar.

On Linux, ESL-Studio may be installed as a Python package, via an
archive (.zip) file. This requires Python (version >= 3.10) to be
installed. It may also be used as an alternative installation on
Window.

This installation archive file may be named
`ESL-Studio-python-{version}-{build_date}.zip` or similar.


Installation
------------

### As a component of ESL

ESL-Studio is available as a component of ESL when you install the
ESL Software simulation product on Windows. It is installed by default.
Simply run the ESL-Pro or ESL-Lite installation setup executable in the
normal way.

Note: You may uncheck the ESL-Studio component in the Windows ESL
installer program if you do not want ESL-Studio installed as a component.

The following sub-sections cover installing an update of ESL-Studio,
which may be the executable update or the Python package update.

We recommend that you use the executable package for Windows. But
ESL-Studio is also available to be installed as a Python package. You
may use this if you encounter problems installing and running the
executable version.

### Executable update - Windows

If there is an existing ESL-Pro or ESL-Lite version 8.3.0.1 or above
installation when you do the ESL-Studio installation, you can choose to install
it in place in that ESL installation. It will replace any existing
ESL-Studio component that may be in the ESL installation folder.

Alternatively, it will install solo, that is independent of an
ESL-Studio that has been installed as a component in an ESL
installation. The ESL-Studio (solo) will get its own Start Menu
short-cut which is independent from the Start Menu short-cut that is
part of the ESL installation (which will still be available).

You should have the installation setup executable (.exe) file, typically
called `ESL-Studio-{version}-{build_date}.exe` (or similar),
accessible somewhere via your directory structure.

To install, invoke the installation file, for example by double
clicking on the file in the Windows Explorer file manager.

The installation setup will guide you though the process of
installation, including asking if you want to install as an ESL
component, if that option is available, or install solo.

### Python package update

You must have Python 3.10 or above installed on your computer.

You should have installation archive file, typically called
`ESL-Studio-python-{version}-{build_date}.zip` (or similar), accessible
somewhere via your directory structure.

The ESL-Studio Python package makes use of the `pip` package management
system (https://pip.pypa.io/) which is normally available automatically
when Python is installed.

We recommend installing the latest wxPython (4.2.0+) python package
prior to running this installation (see
https://wxpython.org/pages/downloads/).

#### Python package update - Linux

Create (if necessary) a directory, for which you have write permissions
(for example `~/Installation`), in which you will install ESL-Studio.

The file manager (for example Nautilus or Nemo) may support .zip files,
in which case you may use it to navigate down to the archive's
`esl-studio` directory, select to extract it and specify the
destination as your installation directory.

Alternatively, in a terminal in that directory, you may use the `unzip`
command (assuming the .zip is in the `~/Downloads` directory):

    cd ~/Installation
    unzip ~/Downloads/ESL-Studio-python-{version}-{build_date}.zip

This will create a subdirectory `esl-studio` in the installation
directory.

In that directory (`~/Installation/esl-studio`), ensure that the
command is executable, then run the command:

    ./install.sh

You should read the guidance instructions and, if required, break out
of the script at a prompt to manually install any prerequisite
packages, and then re-run the script.

Run ESL-Studio with the executable script `./bin/esl-studio`.

#### Python package update - Windows

Create (if necessary) a directory, for which you have write permissions
(for example `%USERPROFILE%\Installation`), in which you will install ESL-Studio.

Extract the contents of the installation archive file into that
directory. This may be done with Windows File Explorer, for example by
navigating down to the archive's`esl-studio` directory, selecting it,
and dragging (to copy) it into your installation directory (in the same
or another Windows File Explorer window).

Use a command prompt (terminal) window in that directory
(for example `%USERPROFILE%\Installation\esl-studio`), and run the command:

    install.cmd

Run ESL-Studio with the executable script `.\bin\esl-studio.cmd`.


Software Support
----------------

### Help

Help documentation for ESL-Studio as packaged with ESL is available
online as part of the ESL Software website Help Pages section. The link
for ESL-Studio is
`https://www.isimsimulation.com/help_pages/esl-studio/`.

You may also access the ESL-Studio online documentation directly from
ESL-Studio via the Help > ESL-Studio Help... menu item.

### Reporting issues

Please look out for 'exception' messages in the message window.

Support is available via e-mail by way of the ESL Software website or
the ESL-Studio online documentation.

When reporting bugs please provide what may be in the message window
and your .eslstudio application file.


Legal Matters
-------------

### License

The software licence for ESL-Studio is the standard MIT License -
SPDX-License-Identifier: MIT

    MIT License

    Copyright (c) 2026 Ryllan J E Kraft

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

### User Responsibility

ESL-Studio is intended for use with the main ESL Software simulation
product. You should carefully read the licence.txt file associated with
the main ESL software (contained in the 'doc' directory) before using
this software with ESL, in particular the section on User
Responsibility.

This section includes:
>   The CUSTOMER hereby acknowledges that simulation software produces results
>   which contain errors. A properly conducted simulation study can make a
>   valuable contribution to decision making processes. On the other hand, an
>   improperly conducted study can give misleading information which may lead to
>   an inappropriate decision and extremely expensive consequences. It is the
>   responsibility of the CUSTOMER to conduct a simulation study in a proper
>   manner, and to perform tests which are necessary to confirm the simulation
>   results are acceptable in the context on any particular decision. Simulation
>   software can be used correctly to produce desired results, or used
>   incorrectly with disastrous results.

***

The ESL-Studio programs are built using the wxPython software based on
wxWidgets (formerly wxWindows). wxPython is licenced under the
"wxWindows Library Licence" (https://wxpython.org/pages/license/). The
following copyright notice was reproduced verbatim from that software's
documentation:

                wxWindows Library Licence, Version 3.1
                ======================================

  Copyright (c) 1998-2005 Julian Smart, Robert Roebling et al

  Everyone is permitted to copy and distribute verbatim copies
  of this licence document, but changing it is not allowed.

                       WXWINDOWS LIBRARY LICENCE
     TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

  This library is free software; you can redistribute it and/or modify it
  under the terms of the GNU Library General Public Licence as published by
  the Free Software Foundation; either version 2 of the Licence, or (at
  your option) any later version.

  This library is distributed in the hope that it will be useful, but
  WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Library
  General Public Licence for more details.

  You should have received a copy of the GNU Library General Public Licence
  along with this software, usually in a file named COPYING.LIB.  If not,
  write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
  Boston, MA 02110-1301 USA.

  EXCEPTION NOTICE

  1. As a special exception, the copyright holders of this library give
  permission for additional uses of the text contained in this release of
  the library as licenced under the wxWindows Library Licence, applying
  either version 3.1 of the Licence, or (at your option) any later version of
  the Licence as published by the copyright holders of version
  3.1 of the Licence document.

  2. The exception is that you may use, copy, link, modify and distribute
  under your own terms, binary object code versions of works based
  on the Library.

  3. If you copy code from files distributed under the terms of the GNU
  General Public Licence or the GNU Library General Public Licence into a
  copy of this library, as this licence permits, the exception does not
  apply to the code that you add in this way.  To avoid misleading anyone as
  to the status of such modified files, you must delete this exception
  notice from such code and/or adjust the licensing conditions notice
  accordingly.

  4. If you write modifications of your own for this library, it is your
  choice whether to permit this exception to apply to your modifications.
  If you do not wish that, you must delete the exception notice from such
  code and/or adjust the licensing conditions notice accordingly.

ESL-Displays - Post Run Analysis
================================

The ESL-Displays program, part of the ESL Software simulation product,
allows you to analyse recorded display files. Typically the display
files will be "prepare" files either generated from the ESL PREPARE
statement or recorded when running a simulation with the ESL-SEC
program.


Starting ESL-Displays
---------------------

You normally start ESL-Displays from ESL-Studio as follows:

-	Use the Simulate > Post Run Analysis... menu item to launch the ESL-Displays
	program directly from ESL-Studio. The ESL-Displays window will
	open without any display files loaded or plots defined.

You may also initiate the ESL-Displays independently from ESL-Studio by invoking
the program directly:

-	You can start ESL-Displays by invoking ESL-Displays from an operating system menu,
	such as the Start Menu, or a short-cut (for example pinned to the
	Desktop). It will then open the ESL-Displays window, again, without
	without any display files loaded or plots defined.

-	You can start ESL-Displays by invoking the executable,
	`esl_displays.exe` (`esl_displays` Linux), installed with ESL-Pro 
	or ESL-Lite in the `esl` `bin` directory of the installation, 
	directly from a file browser application such as Windows Explorer 
	(for example by double clicking). It will then open without display 
	files or plots.

-	You may also open it via a file browser application by double clicking on
	a previously saved ESL-Displays specification file (with extension `.dis`).
	ESL-Displays will then open with the display files loaded, and any
	plots that may have been defined.<br>
	Note: For Linux you would need to have explicitly set up the `.dis`
	file-type to open with ESL-Displays program (`esl_displays`).

-	You can also invoke ESL-Displays by command from a command prompt (terminal)
	window. Normally ESL-Displays is installed on the "PATH" directory, so you just
	need to enter `esl_displays`. Otherwise enter the full path to the executable.
	See below for a description of the ESL-Displays command line options.


Loading Displays
----------------

The main ESL-Displays screen allows you to specify and display plots with
data taken from a set of loaded display files.

You use the "Load" button on the main ESL-Displays screen to load a recorded
display file, and add it to set of them. Loaded display file names appear
in the Display Files panel.

Note: In addition to full "prepare" files, ESL-Displays allows you to load
"tabulate" display files, however these typically do not retain the accuracy
of prepare files.

When a display file is selected in the Display Files panel, its contents are
displayed in the Variables panel from where a plot selection may be made.
Some information, including the number of runs for which the display file data
corresponds appears below the Display Files and Variables panels.

Pressing the "Info" button shows more detailed information from a selected
display file, including any title/subtitle set in the display file.

The "Export" button allows you to export a display file, typically to convert
it to another format such as a Comma Separated Values (CSV) format which may
be imported into other applications such as spreadsheets.


Specifying Plots
----------------

Several plots may be specified and the variables to be displayed in
each selected from the variables from any of the loaded display files.
This allows the comparison of results from different ESL-Studio
sessions, or with experimental data converted to display file format.

The plot's independent variable (used for the X-axis), which is
typically T (for time), determines the primary display file for the
plot. Variables that come from that display file will have values
directly corresponding to the values for the independent variable for
each run in that display file.

When a variable from a different display file is to be incorporated
into the plot, this will lead to an extra "superimposed run" to be
plotted. The superimposed run requires its own independent variable
from the same display file as the new variable. This will generally
correspond to the same name as in the primary display file, typically
"T" (for time again). When the variable is first added, this must be
set in the Details dialog, where subsequently it may be viewed and
changed.

Note: ESL-Displays plot Contents area shows the display file a variable
comes from by a number, the number of the display files loaded into
ESL-Display, followed by a ">" before the variable name. Thus "2>T" is
the variable called T from the 2nd display file and may be the plot's
independent variable, "2>X" is a variable from the same display file,
"3>Y" is a variable taken from a different display file and "3>T" might
be the superimposed run's independent variable.

Note: In fact it may be more complicated as the name may be preceded by
an ESL module name in (round) brackets (parentheses), may include an
annotation (after a ":") and may include a run value or range in curly
(or "squiggly") brackets (braces).

It is important that the range of values for the independent variable
to be used in the superimposed run be appropriate and consistent with
the range in the primary display file for the plot's independent
variable as they will be mapped to the plot's x-axis. Also, the range
of values for all dependent variables (whether from the primary display
file or in superimposed runs) should not differ by too much as they all
are to be plotted on the y-axis.

The "Details" button invokes a Variable Details dialog which allows you
to select the runs for a variable to be plotted against the runs of the
independent variable. For variables that are not in the primary display
file (for which a superimposed run will be plotted), it allows you to
change the superimposed run's independent variable from its own display
file. This dialog also allows you to set or change an annotation for
the variable. This dialog can also be invoked by double-clicking a
variable name.

The "Properties" button invokes a Properties dialog to allow you set up
features for the the plot, including title, axis properties and how the
data points will be plotted.

The "Plot" button opens the plot window, and plots the data as specified for
current plot.

The "Save Data" button allows you to export the data that you have specified
for the current plot to a display file or other format (such as CSV).


Specification files
-------------------

You can save a specification file (with .dis extension) that holds the set
of display files you have loaded and the set of plot definitions you have
set up from the File > Save Specification menu item. The corresponding
File > Load Specification menu item allows you to easily load or change the
display files and plot definitions.


Options/Preferences
-------------------

ESL-Displays has the following option that may be changed via the
File > Options/Preferences menu item:

-	Use external plotting program

###	Use external plotting program

By default ESL-Displays uses an internal plotting dialog. If you select this
option, ESL-Displays will use the standard `plotting` program used in ESL
simulations.

Note: It is possible to change the actual `plotting` program by setting
the ESL_PLOTTING environment variable.

Note: When an external `plotting` program is used ESL-Displays does not
save the position and size (geometry) of the plot windows.


ESL-Displays Command Line Options
---------------------------------

If ESL-Displays is invoked by command, the following options are supported:

	esl_displays [ -fixed ] [ <source-file> ]

Notes: The option may be abbreviated to just the first letter.
The option is case-insensitive.
A pair of dashes (--) may be used instead of the single dash (-).
A forward slash (/) may be used instead of the dash (-) under Windows.

-	source-file:
	A source file may be either an ESL "prepare" file (`.dsp`) or an ESL-Displays
	specification file (`.dis`).

	If an ESL-Displays specification file (`.dis`) is given, the complete
	specification (when the file was saved) is setup.

-	-fixed:
	If this option is given, ESL-Displays will not allow changing the specification
	file path.

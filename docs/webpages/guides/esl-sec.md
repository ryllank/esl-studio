ESL-SEC - Simulation Execution Control
======================================

The ESL-SEC, Simulation Execution Control program, part of the ESL
Software simulation product, allows you to run an ESL simulation
interactively, to change internal values and plot and record values
from runs of the simulation in a simple graphical interface.
In using ESL-SEC you have the option to save all your settings to a Specification file
(extension `.sec`) for future runs of the simulation.

Note: An ESL simulation to run with ESL-SEC should be a STUDY, with a
single model and a simple experiment.


Starting ESL-SEC
----------------

You normally start ESL-SEC from ESL-Studio in one of two ways:

-	To run with the simulation for the current application using the
	Simulate > Run Simulation menu item (or its short-cut on the toolbar).
	In this case the Simulation Setup is handled by ESL-Studio and the
	not available directly in ESL-SEC as such. Also, the ESL-SEC specification
	is maintained with the ESL-Studio application (in its `.eslstudio` file),
	and is not directly available in ESL-SEC. If the application is OK,
	it will generate the ESL code, compile (as specified), and open ESL-SEC
	in a window showing the main control display with the simulation loaded.

-	To launch the ESL-SEC program directly from ESL-Studio use the
	Simulate > Simulation Execution... menu item. The ESL-SEC window will
	open showing the control display but without a simulation loaded. From
	there you can invoke Setup (or File > Setup Simulation menu item) to
	load an ESL simulation or previously prepared ESL-SEC specification.

You may also initiate the ESL-SEC independently from ESL-Studio by invoking
the program directly:

-	You can start ESL-SEC by invoking ESL-SEC from an operating system menu,
	such as the Start Menu, or a short-cut (for example pinned to the Desktop).
	It will then open the ESL-SEC window, again, without a simulation loaded.

-	You can start ESL-SEC by invoking the executable, `esl_sec.exe`
	(`esl_sec` Linux), installed with ESL-Pro or ESL-Lite in the `esl` 
	`bin` directory of the installation, directly from a file browser 
	application such as Windows Explorer (for example by double 
	clicking). It will then open without a simulation loaded.

-	You may also open it via a file browser application by double clicking on
	a previously saved ESL-SEC specification file (with extension `.sec`).
	ESL-SEC will then open with the simulation set up and loaded, and any
	displays (runtime plots, tables or prepare files) that may have been defined.<br>
	Note: For Linux you would need to have explicitly set up the `.sec`
	file-type to open with the ESL-SEC program (`esl_sec`).

-	You can also invoke ESL-SEC by command from a command prompt (terminal)
	window. Normally ESL-SEC is installed on the "PATH" directory, so you just
	need to enter `esl_sec`. Otherwise enter the full path to the executable.
	See below for a description of the ESL-SEC command line options.


Overview
--------

The main ESL-SEC screen allows you to set up a simulation, and also has
a control display to allow you to control the running of the simulation.
It lets you set up simulation parameters, and see and set values for any
ESL variables in the simulation. You can set runtime displays, plots, tables
and record "prepare" files (binary files in a format based on the prepare
file produced by the ESL PREPARE statement). You can invoke advanced simulation
options to take or load snapshot files, run a previously logged driver file
and log a commands to record a driver file. There is also a message area to
report progress and any errors.


Simulation Setup
----------------

The Simulation Setup dialog can be invoked from the "Setup" button and also from
the File > Setup Simulation menu option.

Note: This dialog is not available when running the simulation for an
ESL-Studio application via the Simulate > Run Simulation as ESL-Studio
uses its own Setup view for this.

The simulation may be defined in a number of ways, based on a
simulation file or from an ESL-SEC specification file.

With a simulation file, you specify the Execution Mode which may be:

- Compile and Interpret (`.esl`)
- Compile, Translate, Link and Execute (`.esl`)
- Interpret (`.hcd`)
- Execute (`.exe`) <sub>_(no extension in Linux)_</sub>

The appropriate form of simulation file (`.esl`, `.hcd` or executable), may
be loaded by entering a pathname in the Simulation text area, or via the
browse button, "...", by the Simulation text area.

For the `Compile, Translate, Link and Execute (.esl)` Execution Mode you
must specify C++ or Fortran and may set Extra Options and Additional Link
Objects. This requires ESL-Pro and the appropriate compiler to have been installed.

The Build Command and Run Command text areas will show the commands that
will be used for the build (if required) and to execute the simulation.

An additional Execution Mode, `Custom Run Command`, allows you to specify
an alternate command to execute a simulation, by directly entering the command
in the Run Command text area.

When the simulation has been set up, the simulation may be loaded via the
"Load" button, and the dialog will close. If the simulation has built and
loaded successfully the control display on the main screen will show the simulation
ready to start.

An alternate way to setup a simulation is via a previously saved ESL-SEC
specification file (with `.sec` extension), which may be specified by entering
a pathname in the Specification file text area, or via the browse button,
"...", by the Specification file text area.


Control Panel
-------------

When a simulation has been loaded the main screen's central control panel is
active.

In its initial state, the panel contains the following buttons:

- "Start" - starts simulation running. It changes to "Continue" when simulation
  is in progress.
- "Comm. Break" - interrupts simulation at next communication point.
- "Step Break" - interrupts simulation at next integration step.
- "Abort" - attempts to immediately interrupt the simulation - no restart possible.
- "Rerun" - repeat simulation run.
- "Restart" - complete restart of simulation.
- "End Simulation" - run to the end of the simulation and exit.
- "Finish" - execute terminal region and exit simulation normally.

There is a central radio buttons section specifying when the simulation should
stop after the "Start"/"Continue" button is clicked:

- "End of Run" - to the value of TFIN Simulation Parameter
- "Next Comm. Pt" - to the next communication point
- "Next Step Pt" - to the next integration step point
- "Next Module" - when the simulation changes module (this may not increase
  the simulation time)
- "Time" - to a new value for simulation time that may be set below the button
  (the time must be greater than the current simulation time, but can be
  greater than or less than TFIN).


Simulation Parameters
---------------------

The "Simulation Parameters" button on the main screen opens a dialog that
allows you to set the values for the main simulation parameters.

These parameters, with their default values shown in parenthesis, are:

- TSTART - initial value of T at start of run (0.0)
- TFIN - final value of T at end-of-run (10.0)
- CINT - communication interval (1.0)
- DISERR - discontinuity detection error tolerance (0.0001)
- INTERR - integration error tolerance (0.001)
- ALGO - integration algorithm (RK5).
- NSTEP - number of integration steps in CINT (1).

The options for ALGO are:

- RK5 - fifth-order variable-step integration
- RK4 - fourth-order fixed-step Runge-Kutta integration
- RK2 - second-order fixed-step Runge-Kutta integration
- STIFF2 - second-order stiff integration
- GEAR1 - Gear's variable-step stiff integration
- GEAR2 - Gear's method with diagonal Jacobean
- ADAMS - Adams predictor-corrector integration
- RK1 - Euler first order integration
- LIN1 - Newton-Raphson Linearization routine
- LIN2 - Simplex Linearization routine

Note: LIN1 and LIN2 are used for steady state analysis - see the Steady-State
Analysis section in the ESL Development Guide.


Module Variables
----------------

The "Variables" button on the main screen opens a Variables dialog that allows
the current values of variables and parameters to be displayed and changed.

A list of modules appears in a Modules panel on the left-hand side of the
dialog. If a selected module references any variables, their definitions
are displayed in a Variables panel on the right-hand side. Selecting a variable
will cause that variable's value and type to be displayed at the bottom of
the window. The displayed value can be altered by selecting and overwriting.

The "Show All" button on the Variables dialog opens up a Module dialog
which displays values of all variables in the specified program module.


Runtime Displays
----------------

The "Runtime Displays" button on the main screen opens a Runtime Displays
dialog allows you to select ESL variables in the simulation to directly view
as plots or tables, or to save the data as "prepare" files which may subsequently
be analysed, for example using the ESL-Displays program.

The Runtime Displays dialog is divided into three sections, accessed through
tab controls:

- Plot
- Table
- Prepare

The sections share a number of common control features:

- Name - lists displays that have already been defined for the current application.
  Selecting a name populates the window with the display details.
- New - allows the definition of a new display. Clicking New invokes the
  New Display Definition dialog with an editable default name. Clicking OK
  adds the new name to the Name list.
- Rename/Delete - allows a selected definition to be renamed or deleted.
- Modules/Variables - the Modules panel lists all the modules (models, submodels,
  packages, procedures) that form the active application. Click a specific
  module to list its variables/parameters in the Variables panel.
- Add - select a variable and click Add to copy the selected name into the
  Contents panel (the variable name may be double-clicked with the same result).
  If the variable is an array, you will be prompted to select an element.
- Contents - shows those variables that have been selected for the particular display.
  The first variable, which for a Plot is the independent variable, is initialised
  by default to the Reserved Package time variable T.
- Remove/Move Up/Move Down - deletes/alters the position of an entry in the
  Contents panel.
- Details - allows you set/change an annotation for entry in the Contents panel.
- Properties - invokes an additional window to configure properties specific
  to that type of display.

### Plot

This allows you to plot a number of variables against another (for 
example the simulation time T). The first variable in the Contents 
panel is the independent variable plotted along the x-axis. The other 
variables are plotted up the y-axis. The values are plotted at the 
simulation time as specified by the update interval.

The "Properties" button opens the Plot Properties window allowing the 
following to be defined:

- Title and Subtitle.
- Update interval: Communication Points, Communication Points and Discontinuities or Step Points.
- Show on Load: sets whether to show the plot automatically when the simulation
  is loaded.
- X and Y axes style - including auto-scaling or explicit max & min; axis origin;
  display grid.
- Plot style: line, symbol, line+symbol.

The "Show Display" / "Close Display" button opens or closes a plot window.
Initially the plot shows the specified plot's axes and annotations. The plot is
updated with points as the simulation runs.

### Table

This allows you to view a set of variable values at the simulation time
as specified by the update interval. The table may be shown as a table window
(either listing the variable values or showing the current variable values),
or the data may be sent to an output file.

The "Properties" button opens the Table Properties window allowing the following
to be defined:

- Title and Subtitle.
- Update interval: as for Plot.
- Show on Load (for a window table): sets whether to show the table window
  automatically when the simulation is loaded.
- Create on Load (for an output file table): sets whether to create the
  output file automatically when the simulation is loaded.
- Output: table output is normally to a window, but may be directed to a
  file: either a "tabulate" or Tab file (extension .tab) file or a Comma
  Separated Values or CSV file (extension .csv).
- Style (for a window table): Trend or Monitor. Trend style produces a normal
  scrolling time history of the selected variables. Monitor displays the current
  values only, and updates at the specified rate.

For an output file table, the file name (without extension) defaults to
the name given for the display. This may be set to an explicit file path
via a browse button, "...", or cleared via a clear button, "x".

The "Show Display" / "Close Display" button for a window table opens or closes
a table window.

The "Create Display" / "Close Display" button for an output file table creates
(and may overwrite) the file or closes outputting data to the file.

### Prepare

This allows you to select a set of variables to be recorded for subsequent
post run plotting and analysis, for example using the ESL-Displays program.
This selection is done in the same manner as for Plot and Table.

Values of selected variables are written to a "prepare" file. This is a binary
file in a format based on the prepare file produced by the ESL PREPARE statement.

The "Properties" button opens the Prepare Properties window allowing the following
to be defined:

- Title and Subtitle.
- Update interval: as for Plot & Table.
- Create on Load: sets whether to create the "prepare" file automatically when
  the simulation is loaded.

The "prepare" file name (without extension) defaults to the name given for the
display. This may be set to an explicit file path via a browse button, "...",
or cleared via a clear button, "x".

The "Create Display" / "Close Display" button creates (and may overwrite)
the "prepare" file or closes outputting data to the file.


Advanced Simulation Options
---------------------------

The "Advanced Simulation Options" button on the main screen opens a dialog
that allows you to create or load snapshot files (extension .snp), run a previously
logged driver file and log commands to record a driver file (extension .drv).

### Snapshot Control

When the simulation is stopped, clicking the "Take Snapshot" button in the
Snapshot area of the dialog allows you to specify a snapshot file to which
the current state of the simulation is written in the form of commands to
replicate the state.

The "Load Snapshot" button allows you to open an existing snapshot file for
the current simulation, and the simulation will reset to that saved state.
You may then run the simulation from the snapshot state via the "Start" / "Continue"
button on the main screen control display.

### Driver File Control

You may use the browse button, "..." in the Driver area on this dialog to
load a driver file, and the clear button, "x", to clear it.

Then, if "Run From Driver" is checked, and a driver file name specified,
when the main "Start" / "Continue" button is clicked all subsequent commands
will be taken from the driver file. If the simulation is interrupted, unchecking
the option reverts to manual control. Rechecking allows driver file control
to be recontinued, either from the Next Line or Current Line, as selected.

### Logging

You may use the browse button, "..." in the Log area on this dialog to
specify a driver file for logging, and the clear button, "x", to clear it.

Checking "Log to File" causes all ESL-SEC commands (including display specification
commands) to be written to the specified file, in Append or Overwrite mode,
as selected.


Specification files
-------------------

An ESL-SEC specification file  (with `.sec` extension) holds the holds the simulation
setup (how the simulation is to be invoked), the simulation parameters initial
settings and the runtime display definitions.

You may explicitly save a specification file (if there has been a change) from
the File > Save Specification menu item, which will invoke the Specification
Changed dialog.

The Simulation Setup dialog allows you to easily load a new simulation specification.

ESL-SEC will open the Specification Changed dialog when a change to a specification
might otherwise be lost, as when a new simulation is going to be loaded or when
terminating.

This dialog allows you to change (or set) the specification file 
(unless ESL-SEC has been started with the "-fixed" option - for example 
from ESL-Studio) via the "Change" browse button, "...".

The dialog has areas for sections of the specification that have changed, which
may be Setup, Simulation Parameters and Runtime Displays. You may show more
information about the nature of the changes, and select to save the specification
changes for specific sections. By default all sections are selected to be
saved. The "Save" button performs the save for the selected sections. The
"Don't Save" button discards the changes.


Options/Preferences
-------------------

ESL-SEC has the following options that may be changed via the
File > Options/Preferences menu item:

-	Use external plotting program
-	Prevent overwriting display files
-	Show ESL run command console [Windows]

### Use external plotting program

By default ESL-SEC uses an internal plotting dialog. If you select this
option, ESL-SEC will use the standard `plotting` program used in ESL
simulations.

Note: It is possible to change the actual `plotting` program by setting
the ESL_PLOTTING environment variable.

Note: When an external `plotting` program is used ESL-SEC does not
save the position and size (geometry) of the plot windows.

### Prevent overwriting display files

By default ESL-SEC overwrites "prepare" and table output files when a
display is created if the file exists. If you select this option
ESL-SEC will not overwrite an existing file when you try to create the
display and the values will not be recorded.

### Show ESL run command console

By default, in Windows, ESL-SEC runs simulation programs in the background.
If you select this option the simulation program will run in a Windows
command console.

This is likely to be of use when running a custom command or when there
are additional objects linked in, and diagnostic and other information is
output to the console.


ESL-SEC Command Line Options
----------------------------

If ESL-SEC is invoked by command, the following options are supported:

	esl_sec [ -setup ] [ -fixed ] [ <source-file> ]

Notes: The option may be abbreviated to just the first letter.
The option is case-insensitive.
A pair of dashes (--) may be used instead of the single dash (-).
A forward slash (/) may be used instead of the dash (-) under Windows.

-	source-file:
	A source file may be either an ESL simulation file or an ESL-SEC specification
	file (`.sec`).

	ESL simulation file may be an ESL source file with extension `.esl`,
	an ESL compiled file with extension `.hcd`, or an ESL simulation executable
	file (with `.exe` extension for Windows or no extension for Linux).
	It will be loaded (with the appropriate default setup) directly, unless
	the `-setup` option is given.

	If an ESL-SEC specification file (`.sec`) is given, the complete specification
	(when the file was saved) is set up. The simulation will be loaded directly,
	unless the `-setup` option is given.

-	-setup:
	ESL-SEC will go directly to the Simulation Setup dialog. If a source file has
	been given it will show the simulation set-up appropriately.
	Note, the main ESL-SEC screen will be underneath.

-	-fixed:
	If this option is given, ESL-SEC will not support the Simulation Setup dialog
	and so not allow changing the simulation. This should be used with a source
	file (`.sec` or `.esl`).

	Note: This option is used with ESL-Studio to run the simulation for the application.

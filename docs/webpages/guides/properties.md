View and Simulation Entity Properties
=====================================

The ESL-Studio Properties pane allows you to edit the properties of
views and selected diagram objects.

This section covers the general property features and then covers the
main views, and particular special simulation entities.


General property features
-------------------------

The header area of the Properties pane is usually set with a simple
description or the name for the view or object whose properties are
being shown. It also shows a 'Help' button, which allows you to toggle
on or off a display area at the bottom of the pane to show any "help"
text or hints associated with any selected item on the pane. If this
"help" area is not being shown, the "help" text may be seen as a
"tool-tip" by hovering the mouse pointer over the item.

In some cases, additional buttons may be put in the header area, for
example for subprogram views to add and delete Parameter Variable
properties for the subprogram.

### Basic properties

Properties may be just simple types, such as strings, possibly with
restrictions, or compound properties, such as for a simulation entity
Port, which consists of a set of properties.

Unrestricted string properties are used to let you enter any text, such
as for a description for a particular simulation entity on a diagram,
which may be displayed (as an Annotation) on the diagram.

String properties are shown on the Properties pane in the form of a
text entry box.

Some properties take a value from a discrete a set of strings, which
are usually shown as a "drop-down" list or menu.

Boolean properties are usually shown in the form of a checkbox
(unlike Logical ESL Values).

!!! note
	Most of the properties shown in a pane or view are editable, but
	some are for information, such as a summary for a type of
	simulation entity or the defined Tag for an Attribute.

### ESL Name properties

ESL name properties are strings with restrictions, as they must be
passed as identifiers when the generated ESL code is given to the ESL
Compiler. They must begin with a letter, and contain only letters,
digits and underscores. They are validated to see if they are unique
(in the 24 characters) in the scope (or region) of the generated code
in which they will appear.

In many cases, ESL-Studio may generate a default name, which can be
changed by a valid entry in the text entry box. The default value can
be reinstated, if wanted, by clearing the text entry box. When the
default value is being shown, ESL-Studio may mark the appearance of the
property value by colour (light grey) and with an asterisk (*).

### ESL Value properties

ESL Values are shown as a text entry box (except in the case of
simulation entity Attributes using a 'Source') with additional
validation. Values for Real are usually validated for being acceptable
floating point literal values; Integer type for integer literals; and
Logical types for "TRUE" or "FALSE" (with acceptable abbreviated forms
such as "T" "F" (case-insensitive) or "1" "0"). If a validation fails
at the time of entry it is rejected. If a validation fails for an ESL
Value when some other related property changes (such as the Data Type)
ESL-Studio may mark the appearance of the property value by colour
(a pale orange) and with an exclamation mark (!).

You may want to set an ESL Value literal to a known ESL identifier,
which, to pass the ESL Compiler, would need to be a Constant Variable's
name in use in scope of the current subprogram diagram view. You can
enable this by a button beside the ESL Value text entry box, which
toggles the use of validation. If a value has not been validated,
ESL-Studio may mark the appearance of the property value by colour
(light blue) and with a question mark (?).

There is a special case of ESL Value in simulation entity Attributes
when the value for the attribute, rather than direct text entry, can be
taken from a 'Source'. The value is to be that of an appropriate
variable defined elsewhere in the application. For example, these
include subprogram Parameters or Package Variables, named output Ports,
and certain Reserved variables of the appropriate type. Then the ESL
Value property is shown as a "drop-down" list containing the names of
the variables available in the subprogram scope (that suit this
particular ESL Value).

### Dimensionality properties

There are some properties that allow you, when working with  arrays,
matrices or vectors, to define dimensionality of what will become an
ESL variable in the code generation. These include the 'Dimensions'
property for variable definitions, and in argument simulation
entities, used defining diagram subprogram inputs and outputs. Also,
for ports, the special 'Fix Dimensions' property.

These properties are shown as text entry boxes, that are validated for
strict restrictions as to the textual format the dimensions you can
enter. This format is an extended form of the ESL specification. To fix
the dimensionality, up to 3 dimensions are permitted, and each such
dimension may (optionally) have an integer lower bound (defaults to 1)
and a (required) upper bound.

For example:

| Dimensions	| |
| --- 			| --- |
| 2,-1..1		| A 2 dimensional, 6 element, array (matrix) with first indexed 1 to 2 and second dimension indexed -1 to 1. |
| 0..2			| A 1 dimensional, 3 element, array (vector) elements indexed 0 to 2. |

!!! note
	When joining fixed dimensioned signal lines between ports or
	assigning dimensioned variables as a 'Source' to a fixed dimensioned
	simulation entity attribute value, ESL-Studio normally validates
	just that the number of dimensions and the number of elements in
	each dimension are the same, and does not regard different
	lower/upper bounds as having to be matched.

In some cases, notably for diagram Submodel arguments, and accordingly
for Submodel Calls, the dimensionality can be "generic" - in which one
or more dimensions can be defined as of arbitrary length for the
purposes of connecting or 'Source' assignment. These are defined
textually with an asterisk ('*'), as for the ESL specification.

For example:

| Dimensions	| |
| --- 			| --- |
| 3,*			| A 2 dimensional array (matrix) with three rows each of arbitrary length. |

There is another special "generic" notation, dot-dot-dot ('...', for an
ellipsis) to indicate universal dimensionality, used for the return
result from a Function Call. This output port matches with another port
of any dimensionality, or none, that is a scalar, too.

When assigning initial values, for example in a variable definition or
for a simulation entity property value that has a dimensionality, the
exact number of elements in the array must be specified. The text entry
format to represent array element values is same as for ESL array,
comma separated single values, and the use of a multiplier, an integer
and asterisk (*) before a value, for a sequence of element values,
which may be mixed.

For example, to set element values for an array with six elements, such
as a 2x3 matrix, you could specify:	`1.1, 2.1, 3.1, 1.2, 2.2, 3.2` or
`6 * 100` or `1, 2*3, 2*5, 6`.

It can be important to know or define the internal order of indexing of
elements in a multidimensional array, for instance when assigning
initial values for a matrix that may be used as a lookup table. By
default, ESL-Studio will consider the elements assigned in "row-major"
order, that is the last dimension (column in a 2D matrix) changes most
rapidly and earlier dimensions slower. This is equivalent to enclosing
the array element values in square brackets ([&nbsp;...&nbsp;]). If you want to
use "column-major" order, the transposed order in which the first
dimension changes most rapidly (before the other dimensions) you must
enclose the values with slashes (/&nbsp;...&nbsp;/).

In the example `1.1, 2.1, 3.1, 1.2, 2.2, 3.2` the number before the decimal point is the column (2nd) index and the number after is the row (1st) index.

### Annotations

For some sets of properties, and in particular most compound
properties, it is possible to set an Annotation for the property, a
string of text, appearing on the diagram. The Annotation may be
composed of one or more components joined together in the text. The
text will be set next to its object on the diagram, and move with it,
or in a default location for Annotations for a view.

You may select the Annotation text, and independently move it, relative
to its object, and change some properties of the text. The actual text
will change when the Annotation set of selected components changes or
when any of the property values selected change.

### Variables and Parameters

Variables may be defined as Parameters in a diagram subprogram, by
adding a variable property (with a plus (+) button in the subprogram's
Properties pane header). The same format is used for Package Variables,
added in the same way in a Package view.

A variable is defined by a compound property with the components
described in the table below.

| Name 				| Help/Hints |
| --- 				| --- |
| ESL Name			| An ESL identifier (A..Z 0..9 _) for the variable.<br>The ESL Name must be unique (in 28chars) in its subprogram scope. |
| Description		| Description of this variable.<br>Note: This is a comment in generated ESL. |
| Data Type			| ESL data type for the variable. One of Real, Integer, Logical. |
| Kind of Variable	| One of Parameter, Constant, Variable.<br>Parameter - value can be set interactively before a simulation run but is not changed by the simulation itself.<br>Constant - value fixed here.<br>Variable - value can be changed interactively and can change during a simulation run. |
| Dimensions		| For ESL Array or Matrix (blank for a scalar).<br>For each dimension (up to 3) you can optionally set a lower bound and must set an upper bound.<br>Examples: 3,3 &emsp; 0..2,7..9,-1..1 |
| Value				| Initial value for a variable.<br>For an Array/Matrix, scalar elements (or multiples of them) separated by commas, must have the full number of elements.<br>For a 2D/3D Matrix you may enclose in square brackets for row-major order (the default), or specifically enclose with slashes for column-major order." |

!!! note
	The scope of an ESL Name for a variable refers to the subprogram in
	which it is being defined. Any other variables, for instance in
	packages being "Used" by the subprogram or for named output ports,
	are not permitted to clash with subprogram variable name.


View Properties
---------------

### Program and Model

ESL-Studio always has a permanent view in the main view area to define
the application's Program type and its (main) model.

#### Program properties

Program properties given in the table below.

| Name 					| Help/Hints |
| --- 					| --- |
| Program Type			| Program Type can be one of:<br>- "study" for a normal MODEL (recommended - for use here)<br>- "embedded-program" to generate an EMBEDDED SEGMENT (that may be compiled and embedded in an executable program)<br>- "remote-program" to generate a REMOTE SEGMENT (that may run with a MODEL or program in another process or computer). |
| Program Name			| A name you can give for the Program.<br>This can be any text, but should be short.<br>Note: This is a comment in generated ESL. |
| Program Description	| Description of the Program.<br>Note: This is a comment in generated ESL. |
| Experiment			| Experiment ESL text (source code).<br>This only applies for a STUDY Program (ignored for a remote or embedded program).<br>Note that when this is set it will override any values set in simulation parameters.<br>Use the first button to see and edit the experiment in a multi-line dialog.<br>Use the second button to pre-load the dialog with the default experiment (including simulation parameters and any IO) that would be generated.<br>Clear this experiment property value to reset to the default. |
| Annotations			| Show annotations for the Program on the diagram. |


### Diagram Model properties

The Properties pane header area has plus (+) and minus (-) buttons
labelled 'Parameter' to allow you to add and delete variables to the
Model Parameters section at the bottom.

| Name 			| Help/Hints |
| --- 			| --- |
| ESL Name		| An ESL identifier (A..Z 0..9 _) of this module.<br>The ESL Name must be unique (in 28chars) in the application scope |
| Description	| Description of this module.<br>Note: This is a comment in generated ESL. |
| Annotations	| Show annotations for the module on the diagram. |
| Model Type	| Model Type can be one of:<br>- "model" for a normal MODEL (for use in a Study Program)<br>- "embedded" to generate an EMBEDDED SEGMENT (that may be compiled and used in an Embedded Program)<br>- "remote" to generate a REMOTE SEGMENT (that may run with a MODEL or program for a Remote Program in another process or computer). |
| Use Packages	| Names of packages whose variables are imported and are available for use in this module.<br>Variables in packages must not have the same name as a variable in (or imported into) this module. |

These are followed by any variables defined as Model Parameters.


### Diagram Submodel properties

The Properties pane header area has plus (+) and minus (-) buttons
labelled 'Parameter' to allow you to add and delete variables to the
Submodel Parameters section at the bottom.

| Name 			| Help/Hints |
| --- 			| --- |
| ESL Name		| An ESL identifier (A..Z 0..9 _) of this module.<br>The ESL Name must be unique (in 28chars) in the application scope. |
| Description	| Description of this module.<br>Note: This is a comment in generated ESL. |
| Annotations	| Show annotations for the module on the diagram. |
| Use Packages	| Names of packages whose variables are imported and are available for use in this module.<br>Variables in packages must not have the same name as a variable in (or imported into) this module. |

These are followed by any variables defined as Submodel Parameters.

### Diagram Segment properties

The Properties pane header area has plus (+) and minus (-) buttons
labelled 'Parameter' to allow you to add and delete variables to the
Segment Parameters section at the bottom.

| Name 				| Help/Hints |
| --- 				| --- |
| ESL Name			| An ESL identifier (A..Z 0..9 _) of this module.<br>The ESL Name must be unique (in 28chars) in the application scope. |
| Description		| Description of this module.<br>Note: This is a comment in generated ESL. |
| Annotations		| Show annotations for the module on the diagram. |
| External Segment	| Checkbox to toggle whether the segment is to be declared External (to be evaluated in an Remote Program/External Segment), or to be emulated here. |
| Use Packages		| Names of packages whose variables are imported and are available for use in this module.<br>Variables in packages must not have the same name as a variable in (or imported<br>into) this module. |

These are followed by any variables defined as Segment Parameters.

### Textual Subprogram(s)

Both types of Textual Subprogram views, ESL Import and File Import, have the first two properties:

| Name 			| Help/Hints |
| --- 			| --- |
| Description	| Description of this code import module.<br>Note: This is not used in generated ESL. |
| Code Type		| Code Type will be one of:<br>- "ESL" for one or more internal textual subprograms<br>- "file" for one or more textual subprograms read from a file. |

#### ESL Import properties

An ESL Import view, Code Type "ESL", has an additional property:

| Name 			| Help/Hints |
| --- 			| --- |
| ESL			| ESL text (source code) for the submodel. |

This property, which can only show a portion of the code, has a "..."
button to open a basic multi-line text editor, a modal dialog. However,
in practice, we recommend that it will be preferable to edit the ESL
code in the view itself.

The ESL code is validated when any changes are committed into the
application (either via the modal edit dialog or by changes in the
view). If the changes are rejected the code shown in the view reverts
to the previous accepted contents.

#### File Import properties

A File Import view, Code Type "file", has an additional property:

| Name 			| Help/Hints |
| --- 			| --- |
| File			| ESL file containing the submodel source code. |

This property has a "..." button to select the file. The file contents
is validated when selected, and if the changes are not rejected, the
view is updated (read-only) showing the contents of the file.

### Package properties

A Package, defined in a Package view, has its properties in its view
(in the main view area) rather than in the Properties pane. No
properties are shown in the Properties pane.

The header part of the view has a 'Help' button, which allows you to
toggle on or off a display area at the bottom of the view to show any
"help" text (in a similar way to the Properties pane).

The header part also has plus (+) and minus (-) buttons labelled
'Variable' to allow you to add and delete variables to the Package
Variables section.

The properties for the Package itself are:

| Name 				| Help/Hints |
| --- 				| --- |
| ESL Name			| An ESL identifier (A..Z 0..9 _) for the package.<br>The ESL Name must be unique (in 28chars) in the application scope. |
| Description		| Description  of the Package.<br>Note: This is a comment in generated ESL. |

These are followed by any Package Variables.

### Simulation Parameters properties

The Simulation Parameters properties are shown in a standard view
(in the main view area), available via the View > View Simulation
Parameters menu item.

It allows you to explicitly set specific Simulation Parameters, that is
a specific set of variables defined by the ESL RESERVED package.

By default, these Simulation Parameters will apply to the main model
(as defined in the permanent program and model view). If other Model or
Segment diagram views have been inserted, the Simulation Parameters for
these may be set in this view. The header part of the view has a
"drop-down" list with the names of the modules for which you may set
Simulation Parameters. When you change this module, this view shows the
new set of Simulation Parameters, and also the Properties pane will
show the properties for the corresponding diagram view.

| Name		| Data Type		| Default	| Help/Hints |
| ---		| ---			| ---		| --- |
| TSTART	| Real			| 0.0		| Initial value of T at start of run |
| TFIN		| Real			| 10.0		| Final value of T at end of run |
| CINT		| Real			| 1.0		| Communication interval |
| DISERR	| Real			| 0.0001	| Discontinuity detection error tolerance |
| INTERR	| Real			| 0.001		| Integration error tolerance |
| ALGO		| "drop-down"	| RK5		| Integration algorithm |
| NSTEP		| Integer		| 1			| Number of integration steps in CINT |

Internally in ESL the ALGO (simulation algorithm) Simulation Parameter is held as an Integer, and given as that in the generated ESL code. Here it is shown as a "drop-down" list and, can take the following values:

| ALGO Name							| Integer value |
| ---								| --- |
| RK1 (Euler 1st order)				| 8 |
| RK2 (Runge-Kutta 2nd order)		| 3 |
| RK4 (Runge-Kutta 4th order)		| 2 |
| RK5 (variable-step 5th order)		| 1 |
| GEAR1 (Gear variable-step)		| 5 |
| GEAR2 (Gear diagonal Jacobean)	| 6 |
| STIFF2 (stiff 2nd order)			| 4 |
| ADAMS (Adams predictor-corrector)	| 7 |
| LIN1 (Newton-Raphson trim)		| 21 |
| LIN2 (Simplex trim)				| 22 |

Where any of these are explicitly set, the generated ESL code will
contain these assignments in the "initial" region of the relevant
module's subprogram code. Where not set it will generally take the
default values, or for a Segment, default to the corresponding value in
the Model invoking the segment.

!!! note
	If you defined an experiment for the Program, then if it includes
	any Simulation Parameter assignments, and any of these clash with
	Simulation Parameters explicitly set in this view for a Model, then
	these will supersede those in the Program experiment code.

	The Simulation Parameters view will show a warning message:

		Warning: Program experiment is set
		Simulation Parameters explicitly set here (generated in the ESL "initial" region)
		will override any explicitly set by the program experiment.

### Simulation Setup properties

The Simulation Setup properties are shown in a standard view (in
the main view area), available via the View > View Simulation Setup
menu item. No properties are shown in the Properties pane.

This view allows you to specify display options and features of ESL
code generation and the ESL programs to build and run the application,
which you initiate with the Simulate > Run Simulation menu item.

| Options 						| Help/Hints |
| --- 							| --- |
| Generate only - do not run	| Checkbox to toggle whether the application just be generated, that is it should not be run (if the generation was successful). |
| View generated ESL			| Checkbox to view the generated ESL code. This will be shown in a read-only ESL Text view. |
| Run with Simulation Execution<br>and Control (SEC)	| Checkbox to toggle whether to run the application with ESL-SEC, or to run it directly (in which you will be reminded of a number of restrictions). |
| Execution Command:			| One of:<br>- Compile and Interpret<br>- Compile, Translate, Link and Execute<br>- Custom Run Command. |
| Language | When the execution command is set with the 'Compile, Translate, Link and Execute' option you may select one of the "radio" buttons for "C++" or "Fortran". |
| Extra Options:				|  |
| &emsp;-single					| A checkbox, when the C/C++ language is specified with the 'Compile, Translate, Link and Execute' option, to specify to use single precision compilation and linking. This is required when the C/C++ code is to be linked in with Fortran code generated or compiled here. |
| &emsp;-gcc					| A checkbox, available in the Windows version of ESL-Studio, when the C/C++ language is specified with the 'Compile, Translate, Link and Execute' option, to use the alternate MinGW-W64 compilers and linker in place of the Visual Studio versions. |
| Additional Link Objects:		| Space separated list of base filenames (in the current directory) for binary object files when the execution command is set with the 'Compile, Translate, Link and Execute' option. These object files will be given to the appropriate linker to be linked into the simulation executable. The base filenames should not normally include an extension (except that `.lib` is permitted for Windows Visual Studio object libraries), as the usual extension (`.obj` or `.o`) for the selected language will be used. |
| Build Command:				| This field shows the build command that will be used for the selected execution command option. It cannot be edited. It shows `{AppBase}` for the name of the application generated ESL code - without the `.esl` extension. If the execution command is 'Custom Run Command' it is blank as it assumes a custom command will either include its own build step or rely on it being up to date. |
| Run Command:					| This field shows the run command that will be used for the selected execution command option. When the execution command is 'Custom Run Command' it is initially blank and may be edited. It should be a command (appropriate to the platform). You can pass arguments to a customised run script, including `{AppBase}` or other available Setup pseudo-environment variables. |

| Setup pseudo-environment variables	| Substitution |
| --- 									| --- |
| {AppBase}								| The base name of the application generated ESL code. |
| {gui}									| Will be "-gui" if the 'Run with Simulation Execution' checkbox is checked, otherwise blank. |
| {translation}							| Will be "cc" if the 'Language' "radio" button for C/C++ is on, "f" for Fortran. |
| {single}								| Will be "-single" if the checkbox option 'single' is checked, otherwise blank.  |
| {gcc}									| Will be "-gcc" if the checkbox option 'gcc' (for Windows) is checked, otherwise blank.  |

!!! note

	When you set to run the application directly, that is not with
	ESL-SEC, ESL-Studio will run the code in a background process -
	which has no console to allow text input. The generated code
	will be different in small ways from that generated without this
	limitation. Output from the simulation, including PRINT statements,
	will be shown in the Messages pane.

	When the 'Run with ESL-SEC' checkbox is not checked, the Simulation
	Setup view will show the following reminder message:

		Run simulation directly: Display icons will be generated as PLOT/TABULATE/PREPARE
		statements. READ statements are not allowed.


Simulation Entity Properties
----------------------------

A simulation entity has a basic set of properties, though not all are
always available, from those in the table below.

| Name 			| Help/Hints |
| --- 			| --- |
| Type			| The type of the simulation entity. |
| Summary		| The summary for this type of simulation entity. |
| Help			| Source for help information for this type of simulation entity.<br>Double click property row to open. |
| View			| ESL source code for this type of simulation entity.<br>Double click property row to open. |
| Description	| Description of this specific simulation entity.<br>Note: This is a comment in generated ESL. |
| special subprogram<br>Call property	| To assign (or clear) an appropriate subprogram for the Call - one of<br>Submodel, Segment or Function. |
| Annotations	| Show annotations for the simulation entity on the diagram. |

If you double-click on a simulation entity's Help property (where
available) it will normally open a link to the webpages information on
that entity in your default web browser.

If you double-click on a View property (where available - for an ESL
Library submodel) it will open a read-only ESL Text view in the
main view area showing the code of the submodel.

### Simulation Entity Attributes

A simulation entity may also have a set of Attributes.

An Attribute is defined by a compound property with the components
described in the table below.

| Name 				| Help/Hints |
| --- 				| --- |
| Tag			| Short tag-name for this attribute of the simulation entity. |
| Data Type	| The value for this attribute must have this data-type. |
| ESL Name 	| An ESL identifier (A..Z 0..9 _) for the attribute.<br>The ESL Name must be unique (in 28chars) in its subprogram scope.<br>If not supplied an ESL name will be generated (shown with an asterisk). |
| Source		| Where the value for this attribute comes from:<br>Value - when the actual value is given<br>Parameter - when the module has suitable parameter(s) that can be assigned<br>Name of a Package - when used (imported) into the module<br>RESERVED - when the attribute is assigned the value of a simulation parameter<br>Output - for a named output in the module (of the right data type). |
| Annotations	| Show an annotation for the attribute on the diagram. |

For most of the [standard simulation entities](std-entities.md) the
Properties pane shows the set of attributes predefined for that type of
simulation entity, and in most cases the attribute Name and/or the Tag
should make clear how the simulation will use that attribute. Where
defined, some extra "Help/Hints" information may give guidance on how
to set the attribute. You may view this as a "tool-tip" (by hovering
the mouse pointer over the property component) or in the "help" area at
the bottom of the pane if shown.

!!! tip
	If the simulation entity has a View property, then viewing the
	underlying ESL code (and its comments) may also help to clarify how
	to use the simulation entity.

### Simulation Entity Ports

A simulation entity will usually have a set Ports.

A Port is defined by a compound property with the components described
in the table below.

| Name 				| Help/Hints |
| --- 				| --- |
| Tag				| Short tag-name for this port of the simulation entity (if defined). |
| Data Type			| The value associated with this port has this data-type. |
| ESL Name			| An ESL identifier (A..Z 0..9 _) used an output port in ESL code.<br>The ESL Name must be unique (in 28chars) in its subprogram scope.<br>If not supplied an ESL name will be generated (shown with an asterisk). |
| Description		| Description for the port.<br>Note: This is a comment in generated ESL. |
| Initial Value		| Initial value for the segment call output's variable.<br>Note, this will override any default Initial Value which have been set for a diagram segment on the corresponding Output Argument simulation entity.<br>For an Array/Matrix, scalar elements (or multiples of them) separated by commas, must have the full number of elements.<br>For a 2D/3D Array/Matrix you may enclose in square brackets for row-major order (the default), or specifically enclose with slashes for column-major order. |
| Sign				| Arithmetic sign for the port.<br>For signable ports, for example for Summer or Multiplier types of simulation entities. |
| Fix Dimensions	| Resolve a generic array dimensions to a fixed number of elements per dimension.<br>Set this to resolve an ambiguity - that is if the port is not connected to an input with fixed dimensionality.<br>For a universal dimensionality (as for a function call result) enter "SCALAR" (or "-") to fix to a scalar. |
| Annotations		| Show an annotation for the port on the diagram. |

!!! note
	For ports for a subprogram Call simulation entity, If the
	Description is blank it will inherit from the subprogram's
	argument Arg Description if set (shown with an asterisk).

!!! tip
	There is an 'Id' port annotation for the port's identifier (number)
	which can help show which port is which on a simulation entity,
	particularly when the simulation entity has been rotated or
	mirrored.


Special Simulation Entities
---------------------------

### Subprogram Calls and Code Inserts

Subprogram Call simulation entities produce calls of a specified
subprogram (Submodel, Segment or Function) when the ESL code is
generated. The subprogram may be a diagram or a textual (code import)
one.

The ports and attributes of a Call are determined by the "signature" of
the subprogram:

- an input argument normally shows as an input port on the simulation
  entity;
- however, if the input argument, defined (in a diagram) by an Input
  Argument has its Attribute checkbox check, or if defined by ESL
  textual code CONSTANT, then it shows as an attribute of the
  simulation entity;
- an output argument shows as an output port.

!!! tip
	If you change the subprogram for a subprogram Call, or change its
	subprogram's "signature", the subprogram Call simulation entity's
	appearance will change accordingly. If the Call has any connected
	ports, then, while ESL-Studio will try to preserve any connections
	it considers correspond from the old "signature" to the new one, it
	may not do exactly as you would wish. We recommend you do not make
	a complex set of connections to any Calls unless you are satisfied
	the "signature" of their subprograms is unlikely to be
	significantly changed.

#### Submodel Call

The Submodel Call simulation entity has an additional entity property:

| Name 		| Help/Hints |
| --- 		| --- |
| Submodel 	| The submodel for the submodel call. |

#### Segment Call

The Segment Call simulation entity has an additional entity property:

| Name 		| Help/Hints |
| --- 		| --- |
| Segment	| The segment for the segment call. |

It also has special Segment Call Control properties:

| Name 				| Tag		| Help/Hints |
| --- 				| --- 		| --- |
| Frequency of calls| frequency	| Frequency of communication region calls for the segment - a multiple of communication interval (CINT).<br>Note: The segment should have its Simulation Parameter CINT set to this value multiplied by the CINT of the calling module. |
| Time delay		| delay		| Time delay before making the first call to the segment.<br>Note: The segment should have its Simulation Parameter TSTART set to this value. |

#### Function Call

The Function Call simulation entity has an additional entity property:

| Name 		| Help/Hints |
| --- 		| --- |
| Function	| The function for the function call. |

#### Code Insert

The Code Insert simulation entity allows you to plant ESL code in the
code that is generated for the subprogram (Model, Segment, Submodel)
diagram that it is in.

It has an additional entity Code Insert Properties:

| Name 				| Help/Hints |
| --- 				| --- |
| ESL Region		| ESL region in generated code to insert the code.<br>Note: The "terminal" and "analysis" regions are only applicable in a MODEL subprogram. |
| Insert Position	| Insert the code at the beginning or end of the region - that is before or after generated code for the region.<br>The default is at the end. |
| ESL Code			| The code insert's ESL text (source code).<br>Press the button to see and edit the code in a multi-line dialog.<br>This code is not validated in ESL-Studio (but is checked by the ESL compiler when the code is generated).<br>Note: Procedural code to be inserted in the "dynamic" region will have to be in a WHEN statement or PROCEDURAL model block. |
| Output Ports		| A semicolon-separated set of ESL Data Types for the output ports (valid for dynamic, communications & step regions).<br>Note: You must set the ESL Names for these ports to use in the ESL Code of this code insert. |


### Subprogram Arguments

Argument simulation entities are used to define the inputs and outputs
for a diagram subprogram (that is the "signature" of the
subprogram).

#### Input Arguments

The Real Input, Integer Input, and Logical Input simulation entities
have special Argument Attributes properties:

| Name 				| Tag		| Help/Hints |
| --- 				| --- 		| --- |
| Arg Name 			| ARG 		| An ESL identifier (A..Z 0..9 _) for the argument in the generated ESL subprogram.<br>The Arg Name should be unique in 18chars in its subprogram (to allow for its use in generated variables).<br>If not supplied one will be generated (shown with an asterisk). |
| Arg Description 	| ARGDESC 	| Description for this subprogram input port or attribute |
| Dimension 		| ARGDIMS	| For Array or Matrix. |
| Attribute 		| ATTR 		| If Attribute is set the argument will be an attribute of the subprogram call, otherwise it will be an input port. |

#### Output Arguments

The Real Output, Integer Output, and Logical Output simulation entities
have special Argument Attributes properties:

| Name 				| Tag		| Help/Hints |
| --- 				| --- 		| --- |
| Arg Name 			| ARG 		| An ESL identifier (A..Z 0..9 _) for the argument in the generated ESL subprogram.<br>The Arg Name should be unique in 18chars in its subprogram (to allow for its use in generated variables).<br>If not supplied one will be generated (shown with an asterisk). |
| Arg Description 	| ARGDESC 	| Description for this subprogram output port. |
| Dimensions 		| ARGDIMS 	| For Array or Matrix. |
| Initial Value 	| INIT 		| Initial value for the variable for the segment call corresponding to this output argument. |

### Constant Inputs

The Constant Real, Constant Integer, and Constant Logical simulation
entities have special Attribute properties:

| Name 				| Tag			| Help/Hints |
| --- 				| --- 			| --- |
| Value 			| K 			| Constant value consistent with the basic ESL datatype (Real) and the specified dimensions (if for an array).<br>Default 1.0 |
| Dimensions 		| dimensions	| For ESL Array or Matrix (blank for a scalar).<br>For each dimension (up to 3) can optionally set lower bound and must set an upper bound.<br>Examples: 3,3 &emsp; 0..2,7..9,-1..1 |

### Transfer Function

The Transfer Function simulation entity has special Transfer Function
Attributes:

| Name 					| Tag				| Help/Hints |
| --- 					| --- 				| --- |
| Transfer Function		| TF				| Express the transfer function in the ESL notation for the Laplace transform with Laplacian operator &quot;s&quot; (and using ESL Names for variables).<br>Default 1/(s+1) |
| Initial Conditions	| ICS				| One or more state variable initial conditions (not more than the number of states) - separate with comma.<br>Examples: 0.1 &emsp; YD0<br>Default 0.0 |
| Differential Equations| TF-differential	| Checkbox to toggle whether to generate Transfer Function as differential equations if selected, else generate as an ESL TRANSFER statement.<br>Default False |

Standard Menu
=============

This section covers the ESL-Studio menubar menus with their menu items.

File
----
**New**														  			: Clears ESL-Studio to creates a new application<br>
**Open...**													  			: Lets you select and opens an existing ESL-Studio application<br>
**Save**														 		: Saves the ESL-Studio application with the current application
																		  filename<br>
**Save As...**												   			: Lets you select to save the ESL-Studio application with new
																		  application filename<br>
**Print/Save Diagram...**												: Opens the Print/Save Diagram dialog to let you define an
																		  area on the diagram to be printed or saved as an image<br>
![Print/Save Diagram dialog](images/print-save-diagram-dialog.png "Print/Save Diagram dialog")<br>
**Page Setup...**														: Shows the standard Page Setup dialog to let you set the page
																		  settings for printing<br>
**Print Preview...**											 		: Shows a preview printout for the current diagram or text view<br>
**Print View...**														: Shows the standard Print dialog to set where to print the current
																		  diagram or text view<br>
**View Source File...**										  			: Lets you select to open a source (text) file for viewing<br>
**Open Text Editor...**													: Opens the external Text Editor (which may be specified in the Preferences/Options dialog)<br>
**Preferences/Options...**												: Opens the Preferences/Options dialog - this has tabs: General,
																		  Application, Diagrams, Views & Advanced<br>
![Preferences/Options dialog General tab](images/options-dialog-general.png "Preferences/Options dialog General tab")<br>
**Application History >**<br>
-	**Clear Application History**										: Clears the history list of recent applications<br>
-	list of recently loaded `.eslstudio` application files				: Lets you to select one to reload into ESL-Studio<br>
**Exit**																: Exits ESL-Studio<br>

Edit
----
**Undo**																: Undoes the last editing action<br>
**Redo**																: Redoes the previously undone action<br>
**Cut**																	: Cuts the selection and moves it to the clipboard<br>
**Copy**																: Copies the selection to the clipboard<br>
**Paste**																: Pastes the clipboard contents onto the diagram<br>
**Delete**																: Deletes the current selection<br>
**Select All**															: Selects all objects<br>
**Flip >**	<br>
-	**Left/Right**														: Flips the selected diagram objects horizontally<br>
-	**Up/Down**															: Flips the selected diagram objects vertically<br>
**Rotate >**	<br>
-	**Left 90 Degrees**													: Rotates the selected diagram objects 90 degrees left<br>
-	**180 Degrees**														: Rotates the selected diagram objects 180 degrees<br>
-	**Right 90 Degrees**												: Rotates the selected diagram objects 90 degrees right<br>

View
----
**View Toolbar**														: Shows/hides the toolbar<br>
**View Application**													: Shows/hides the Application pane - tree view of the application<br>
**View Elements**														: Shows/hides the Elements pane - available simulation elements<br>
**View Messages**														: Shows/hides the Messages pane - the message display area<br>
**View Properties**														: Shows/hides the Properties pane<br>
**View Simulation Parameters**											: Shows/hides the model's Simulation Parameters view
																		  - they determine how the simulation will be run<br>
**View Simulation Setup**												: Shows/hides the simulation Setup view<br>
**Clear Messages**														: Clears the contents of the Messages pane<br>
**Zoom...**																: Opens the Zoom Settings dialog to allow you to change
																		  the diagram zoom factor<br>
![ESL-Studio Zoom dialog](images/zoom-dialog.png "ESL-Studio Zoom dialog")<br>
**Zoom Reset**															: Resets diagram zoom factor to normal (100)<br>
**Zoom All**															: Zooms diagram to show all elements<br>
**Zoom Selected**														: Zooms diagram to show all selected elements<br>

Insert
------
**Submodel Diagram**													: Inserts a new submodel diagram view into the application<br>
**Textual Submodel >**<br>
-	**ESL**																: Inserts a new ESL textual submodel view into the application<br>
-	**File**															: Inserts a new file textual submodel view into the application<br>
**Package**																: Inserts a new variables package view into the application<br>

Simulate
--------
**Run Simulation**														: Builds and runs the ESL simulation for the application
																		  as defined in the Setup view - it should start ESL-SEC for
																		  the simulation (if so defined and application was valid
																		  - generated its ESL code and compiled OK)<br>
**View Simulation Setup**												: Shows/hides the simulation Setup view<br>
**Simulation Execution...**												: Launch ESL-SEC, to run another simulation<br>
**Post Run Analysis...**												: Launch the ESL-Displays for post run analysis<br>

Help
----
**ESL-Studio Help...**													: Displays the ESL-Studio Help Page (website)<br>
**ESL Help...**															: Displays the ESL Help file (installed locally)<br>
**ESL Documents...**													: Displays the ESL Documents (website)<br>
**Check ESL-Studio Updates...**											: Check for any updates to this version of ESL-Studio<br>
**Check ESL Updates...**												: Check for any updates to the current version of ESL<br>
**About...**															: Shows information about ESL-Studio (version & licence)<br>



Diagram Background Context Menu
===============================

This section covers the context menu for a diagram, for a right click
on the background.

**Paste**																: Pastes the clipboard contents onto the diagram<br>
**Insert Simulation Elements >**<br>
-	**Linear Operators >**<br>
-	-	**Insert Transfer Function**									: Insert a Transfer Function entity<br>
-	-	**Insert Constant Multiplier**									: Insert a Constant Multiplier entity<br>
-	-	**Insert Integrator**											: Insert an Integrator entity<br>
-	**Arithmetic Operators >**<br>
-	-	**Insert Summer**												: Insert a Summer entity<br>
-	-	**Insert Summer 3**												: Insert a Summer 3 entity<br>
-	-	**Insert Multiplier**											: Insert a Multiplier entity<br>
-	-	**Insert Divider**												: Insert a Divider entity<br>
-	**Insert Submodel Call**											: Insert a Submodel Call<br>
**Insert Basic Elements >**<br>
-	**Insert Rectangle**												: Insert a rectangle into the diagram<br>
-	**Insert Ellipse**													: Insert an ellipse into the diagram<br>
-	**Insert Line**														: Insert a line into the diagram<br>
-	**Insert Text**														: Insert text into the diagram<br>
-	**Insert Image**													: Insert an image into the diagram<br>
-	**Insert Polyline**													: Insert a polyline (open polygon) into the diagram<br>
-	**Insert Polygon**													: Insert a polygon into the diagram<br>
-	**Insert Spline**													: Insert a spline into the diagram<br>


Simulation Entity Context Menu
==============================

This section covers context menu for a (normal) simulation entity, for
a right click on the object in the diagram.

**Cut**																	: Cuts the object and moves it to the clipboard<br>
**Copy**																: Copies the object to the clipboard<br>
**Delete**																: Deletes the object<br>
**Select All**															: Selects all objects<br>
**Flip >**	<br>
-	**Left/Right**														: Flips the selected object horizontally<br>
-	**Up/Down**															: Flips the selected object vertically<br>
**Rotate >**<br>
-	**Left 90**										  					: Rotates the selected object 90 degrees left<br>
-	**180**																: Rotates the selected object 180 degrees<br>
-	**Right 90**														: Rotates the selected object 90 degrees right<br>

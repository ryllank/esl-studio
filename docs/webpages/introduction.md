Introduction to ESL-Studio
==========================

ESL-Studio is an integrated development environment for creating ESL
simulations using block diagrams and ESL source code. It may be used
ESL Software's simulation product - either ESL-Pro or ESL-Lite.

Using ESL-Studio's graphical user interface you can manage each stage
of the simulation activity.

ESL-Studio provides the following facilities:

- Multi-window graphical block diagram editor for model construction.
- Inclusion of ESL coded submodels where appropriate.
- Interactive control of simulation execution (via the ESL-SEC program)
  with run-time graph plotting.
- Display manager with post-run graph plotting (via the ESL-Displays
  program).
- Sophisticated profile features allow themes for diagram appearance and
  for standard and library simulation entities.

ESL-Studio includes a graphical editor for block diagram style model
descriptions, while allowing textual ESL code to be used where
appropriate (for example to describe highly non-linear elements). You
select standard simulation entities and interconnect them on a block
diagram to build up the simulation description. ESL submodels can be
created and included in a diagram through a special submodel element.

Once you have created a simulation program (graphically, textually or a
combination of both), compilation is initiated from ESL-Studio.
You may then execute the compiled program immediately through an
interpreter, or, for ESL-Pro, you have the option to further translate
it to C++ or FORTRAN. The resulting executable program may then be run
from ESL-Studio.
In either case, execution is managed by the ESL-SEC (Simulation
Execution Control) program, part of the ESL Software simulation
product, which provides run-time control of the simulation.
You have access to all program variables and parameters from the
ESL-SEC program. This includes simulation parameters such as the
communication interval, final simulation time, choice of integration
algorithm and error tolerances. All variables and parameters can be set
and changed dynamically.
You can specify graphical and tabulated output on your block diagram
through the use of special display icon simulation entities or
alternatively from the Runtime Displays option of ESL-SEC. You can log
all run time commands and output specifications to a driver file that
can be used at a later time to repeat simulation scenarios.

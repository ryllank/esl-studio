Standard Simulation Entities
============================

In ESL-Studio, simulation entities are represented by graphical objects
(icons) that may be placed on a simulation block diagram and may be
connected up with signal lines.

These are available from the Elements pane, in the form of a classified
tree view.

This webpage covers the standard set of simulation entities provided in 
ESL-Studio with the order and classified as in the standard Elements 
pane tree view.


## Common Elements

### Linear Operators

#### ![icon](elementicons/transfunction.png) &nbsp; &nbsp; Transfer Function {#Transfer_Function}
Specifies a Laplace Transfer Function (generates an ESL TRANSFER statement or an equivalent set of differential equations).
<br>Special Transfer Function Attributes: Transfer Function, Initial Conditions, Differential Equations.

#### ![icon](elementicons/constmultiplier.png) &nbsp; &nbsp; Constant Multiplier {#Constant_Multiplier}
Multiplies input by a constant (y = K * x).

#### ![icon](elementicons/integrator.png) &nbsp; &nbsp; Integrator {#Integrator}
Integral of input with respect to time.
<br>Note: This simulation entity is in two sections in the Elements tree view: Common Elements | Linear Operators and Library (Linear) | Integrators.

### Arithmetic Operators

#### ![icon](elementicons/summer.png) &nbsp; &nbsp; Summer {#Summer}
Sum of two signed inputs (x + y).

#### ![icon](elementicons/summer3.png) &nbsp; &nbsp; Summer 3 {#Summer_3}
Sum of three signed inputs (x + y + z).

#### ![icon](elementicons/multiplier.png) &nbsp; &nbsp; Multiplier {#Multiplier}
Product of signed inputs (x * y).

#### ![icon](elementicons/divider.png) &nbsp; &nbsp; Divider {#Divider}
Quotient of signed inputs (x / y).

### Logical Operators

#### ![icon](elementicons/not.png) &nbsp; &nbsp; Logical Negation {#Logical_Negation}
Logical NOT (negation) of input.

#### ![icon](elementicons/and.png) &nbsp; &nbsp; Logical And {#Logical_And}
Logical AND (conjunction) of two inputs.

#### ![icon](elementicons/or.png) &nbsp; &nbsp; Logical Or {#Logical_Or}
Logical OR (disjunction) of two inputs.

### Standard Functions

#### ![icon](elementicons/sine.png) &nbsp; &nbsp; Sine {#Sine}
Sine of input in radians.

#### ![icon](elementicons/cosine.png) &nbsp; &nbsp; Cosine {#Cosine}
Cosine of input in radians.

#### ![icon](elementicons/tangent.png) &nbsp; &nbsp; Tangent {#Tangent}
Tangent of input in radians.

#### ![icon](elementicons/absolute.png) &nbsp; &nbsp; Absolute {#Absolute}
Absolute value of input.
<br>This is the modelling version of the standard function which treats
changes in output as discontinuities (uses Library submodel ABSX).

#### ![icon](elementicons/asine.png) &nbsp; &nbsp; Arc Sine {#Arc_Sine}
Arcsine of input.

#### ![icon](elementicons/acosine.png) &nbsp; &nbsp; Arc Cosine {#Arc_Cosine}
Arccosine of input.

#### ![icon](elementicons/atangent.png) &nbsp; &nbsp; Arc Tangent {#Arc_Tangent}
Arctangent of input.

#### ![icon](elementicons/atangent2.png) &nbsp; &nbsp; Arc Tangent 2 {#Arc_Tangent_2}
Arctangent of two inputs (x / y).

#### ![icon](elementicons/exponential.png) &nbsp; &nbsp; Exponential {#Exponential}
Exponential of input (e ** x).

#### ![icon](elementicons/naturallog.png) &nbsp; &nbsp; Natural Logarithm {#Natural_Logarithm}
Natural logarithm of input.

#### ![icon](elementicons/base10log.png) &nbsp; &nbsp; Base 10 Logarithm {#Base_10_Logarithm}
Logarithm to base 10 of input.

#### ![icon](elementicons/power.png) &nbsp; &nbsp; Power {#Power}
Raises first input to value of second input (exponentiation) (x ** y).

#### ![icon](elementicons/squareroot.png) &nbsp; &nbsp; Square Root {#Square_Root}
Square root of absolute value of real input (uses Library submodel
SQRTX).

#### ![icon](elementicons/integer.png) &nbsp; &nbsp; Integer {#Integer}
Output is the integer value of real input.
<br>This is the modelling version of the standard function which treats
changes in output as discontinuities (uses Library submodel INTX).

## Input/Output

### Inputs

#### ![icon](elementicons/stepinput.png) &nbsp; &nbsp; Step Input {#Step_Input}
Generates a step function (includes Library submodel STEPP).

#### ![icon](elementicons/sinusoidal.png) &nbsp; &nbsp; Sine Input {#Sine_Input}
Generates a sine wave of specified amplitude, frequency, and phase.

#### ![icon](elementicons/rampinput.png) &nbsp; &nbsp; Ramp Input {#Ramp_Input}
Generates a ramp of unit slope after optional initial time delay (uses
Library submodel RAMP).

#### ![icon](elementicons/squareinput.png) &nbsp; &nbsp; Square Input {#Square_Input}
Generates a square wave of specified amplitude, M/S ratio, period, and
initial time-delay (includes Library submodel MODULT).

#### ![icon](elementicons/timeinput.png) &nbsp; &nbsp; Time Input {#Time_Input}
Simulation time (T).

#### ![icon](elementicons/impulse.png) &nbsp; &nbsp; Impulse Input {#Impulse_Input}
Generates a periodic train of impulses with a controlled delay before
the first pulse (uses Library submodel IMPUL).

#### ![icon](elementicons/pulse.png) &nbsp; &nbsp; Pulse Input {#Pulse_Input}
Generates a unit pulse of specified duration (uses Library submodel PULSE).

#### ![icon](elementicons/constreal.png) &nbsp; &nbsp; Constant Real {#Constant_Real}
REAL constant value.

#### ![icon](elementicons/constinteger.png) &nbsp; &nbsp; Constant Integer {#Constant_Integer}
INTEGER constant value.

#### ![icon](elementicons/logicaltrue.png) &nbsp; &nbsp; Constant True {#Constant_True}
LOGICAL constant with value TRUE.

#### ![icon](elementicons/logicalfalse.png) &nbsp; &nbsp; Constant False {#Constant_False}
LOGICAL constant with value FALSE.

#### ![icon](elementicons/constlogical.png) &nbsp; &nbsp; Constant Logical {#Constant_Logical}
LOGICAL constant value determined by attribute.

### Input Arguments

Special Argument Attributes: Arg Name, Arg Description, Dimensions, Attribute.

#### ![icon](elementicons/realinput.png) &nbsp; &nbsp; Real Input {#Real_Input}
REAL input value to a diagram subprogram (submodel or segment).

#### ![icon](elementicons/integerinput.png) &nbsp; &nbsp; Integer Input {#Integer_Input}
INTEGER input value to a diagram subprogram (submodel or segment).

#### ![icon](elementicons/logicalinput.png) &nbsp; &nbsp; Logical Input {#Logical_Input}
LOGICAL input value to a diagram subprogram (submodel or segment).

### Output Arguments

Special Argument Attributes: Arg Name, Arg Description, Dimensions.

#### ![icon](elementicons/realoutput.png) &nbsp; &nbsp; Real Output {#Real_Output}
REAL output value from a diagram subprogram (submodel or segment).

#### ![icon](elementicons/integeroutput.png) &nbsp; &nbsp; Integer Output {#Integer_Output}
INTEGER output value from a diagram subprogram (submodel or segment).

#### ![icon](elementicons/logicaloutput.png) &nbsp; &nbsp; Logical Output {#Logical_Output}
LOGICAL output value from a diagram subprogram (submodel or segment).


## Library (Linear)

#### ![icon](elementicons/derivative.png) &nbsp; &nbsp; Derivative {#Derivative}
First-order derivative (uses Library submodel DERIV).

### Laplace Operators

#### ![icon](elementicons/complexpole.png) &nbsp; &nbsp; Complex Pole {#Complex_Pole}
Second order lag (uses Library submodel CMPXPL).

#### ![icon](elementicons/leadlag.png) &nbsp; &nbsp; Lead Lag {#Lead_Lag}
Lead-lag transfer function (uses Library submodel LEDLAG).

#### ![icon](elementicons/realpole.png) &nbsp; &nbsp; Real Pole {#Real_Pole}
First order lag (uses Library submodel REALPL).

### Integrators

#### ![icon](elementicons/integrator.png) &nbsp; &nbsp; Integrator
Integral of input with respect to time.
<br>Note: This simulation entity is in two sections in the Elements tree view: Common Elements | Linear Operators and Library (Linear) | Integrators.

#### ![icon](elementicons/limitedintegrator.png) &nbsp; &nbsp; Limited Integrator {#Limited_Integrator}
Integrator in which output is bounded between lower and upper limits
(uses Library submodel LIMINT).

#### ![icon](elementicons/logicalintegrator.png) &nbsp; &nbsp; Logical Integrator {#Logical_Integrator}
Logically controlled integrator - the integrator's mode of operation is
controlled by logical input signals (uses Library submodel LOGINT).

#### ![icon](elementicons/fouriertransform.png) &nbsp; &nbsp;  Fourier Transform {#Fourier_Transform}
Fourier integrator
<br>Calculates the rms magnitude and angle of a specified harmonic
component of the Fourier series for an input signal.
<br>Prints stats at the end of each cycle (uses Library submodel FOURINT).

### Controllers

#### ![icon](elementicons/picontrol.png) &nbsp; &nbsp; PI Controller {#PI_Controller}
Proportional plus integral (PI) controller (uses Library submodel
PICONT).

#### ![icon](elementicons/pidcontrol.png) &nbsp; &nbsp; PID Controller {#PID_Controller}
Three term (PID) controller with limited output and integral
anti-windup (uses Library submodel PIDCONT).

#### ![icon](elementicons/pidcontrol1.png) &nbsp; &nbsp; PID Controller 1 {#PID_Controller_1}
Three term (PID) controller with limited output, anti-windup and
deadspace (uses Library submodel PIDCONT1).


### Timers

#### ![icon](elementicons/timer.png) &nbsp; &nbsp;  Timer {#Timer}
Measures the simulation time which has elapsed since it was reset by a
logical input (uses Library submodel TIMER).


## Library (Nonlinear)

### Oscillators

#### ![icon](elementicons/bistable.png) &nbsp; &nbsp; Bistable {#Bistable}
Bistable storage device - stores logical input as the clock input
becomes TRUE (uses Library submodel BISTBL).

#### ![icon](elementicons/modulator.png) &nbsp; &nbsp; Modulator {#Modulator}
Pulse width modulator - generates a periodic logical pulse train with
the mark/space ratio being controlled by an input variable and an
optional time delay before the first transition (uses Library submodel
MODULT).

#### ![icon](elementicons/monostable.png) &nbsp; &nbsp; Monostable {#Monostable}
Output set TRUE when input becomes positive and remains set for at
least a time period specified by attribute, or until the input variable
becomes negative (uses Library submodel MONO).

### Comparators

#### ![icon](elementicons/comparator.png) &nbsp; &nbsp; Comparator {#Comparator}
Logical output true if inputs (x >= y).

#### ![icon](elementicons/backlash.png) &nbsp; &nbsp; Backlash {#Backlash}
Comparator with backlash - logical output becomes TRUE when input x
greater than or equal to upper limit and FALSE when less than lower
limit (uses Library submodel COMPB).

### Digitisers

#### ![icon](elementicons/delay.png) &nbsp; &nbsp; Delay {#Delay}
Periodically samples a continuous input signal and delays output of the
sampled signal for a fixed period of time, for example a pipeline delay
(uses Library submodel DELAY).

#### ![icon](elementicons/firstorderhold.png) &nbsp; &nbsp; First Order Hold {#First_Order_Hold}
Periodically samples a continuous input signal and produces an output
of the last sample modified with a slope calculated by the previous two
samples (uses Library submodel FHOLD).

#### ![icon](elementicons/quantizer.png) &nbsp; &nbsp; Quantizer {#Quantizer}
Quantizes a continuous input signal into values which are integer
multiples of a specified quantization value (uses Library submodel
QNTZR).

#### ![icon](elementicons/sampleandhold.png) &nbsp; &nbsp; Sample and Hold {#Sample_and_Hold}
Periodically samples a continuous input signal and outputs the value at
the last sampling point (uses Library submodel SAMHLD).

#### ![icon](elementicons/zeroorderhold.png) &nbsp; &nbsp; Zero Order Hold {#Zero_Order_Hold}
Output holds value of x input when hold input becomes TRUE.
<br>While hold is FALSE output is equal to input (uses Library submodel ZHOLD).

### Limiters

#### ![icon](elementicons/deadspace.png) &nbsp; &nbsp; Deadspace {#Deadspace}
Simulates the effect of a 'deadspace'.
<br>Output y = 0.0, if LL &lt; x &lt; UL; y = x-UL, if x >= UL; y = x-LL, 
if x &lt;= LL (uses Library submodel DEADSP).

#### ![icon](elementicons/hysterisis.png) &nbsp; &nbsp; Hysteresis {#Hysteresis}
Implements a pure hysteresis or backlash function (uses Library
submodel HSTRSS).

#### ![icon](elementicons/limiter.png) &nbsp; &nbsp; Limiter {#Limiter}
The output follows the input provided the input remains between lower
and upper limits.
<br>The output is held at a limit if the input goes outside the limits
(uses Library submodel LIMIT).

### Misc

#### ![icon](elementicons/rectifier.png) &nbsp; &nbsp; Rectifier {#Rectifier}
The operation of a Silicon Controlled Rectifier (SCR) is represented
for given inputs of current, voltage and gate pulse (uses Library
submodel RECT).

#### ![icon](elementicons/friction.png) &nbsp; &nbsp; Friction {#Friction}
Determines the friction between sliding surfaces from applied force and
relative velocity (uses Library submodel COULOMB).

#### ![icon](elementicons/switch.png) &nbsp; &nbsp; Switch {#Switch}
Switch between two REAL inputs depending on LOGICAL control input.

#### ![icon](elementicons/functiongenerator.png) &nbsp; &nbsp; Function Generator {#Function_Generator}
Generates function values from a one-, two- or three- dimension table
(uses Library submodel FG3D).


## Subprogram Calls

#### ![icon](elementicons/submodel.png) &nbsp; &nbsp; Submodel Call {#Submodel_Call}
Calls a submodel.
<br>Special attribute: Submodel.
<br>Attributes and Ports are determined by the Submodel arguments.

#### ![icon](elementicons/segment.png) &nbsp; &nbsp; Segment Call {#Segment_Call}
Calls a segment.
<br>Special attribute: Segment.
<br>Special Segment Call Control attributes: Frequency of call, Time delay.
<br>Attributes and Ports are determined by the Segment arguments.

#### ![icon](elementicons/function.png) &nbsp; &nbsp; Function Call {#Function_Call}
Calls a function.
<br>Special attribute: Function.
<br>Attributes and Ports are determined by the Function arguments.


#### ![icon](elementicons/codeinsert.png) &nbsp; &nbsp; Code Insert {#Code_Insert}
Puts a procedural code insert in the generated ESL.
<br>Special Code Insert Properties: ESL Region, Insert Position, ESL Code, Output Ports.
<br>Ports are determined by the Output Ports attribute.


## Display Icons

#### ![icon](elementicons/plot.png) &nbsp; &nbsp; Plot {#Plot}
Display a runtime plot by connecting instrumentation lines to outputs.

#### ![icon](elementicons/table.png) &nbsp; &nbsp; Table {#Table}
Display a runtime table by connecting instrumentation lines to outputs.

####![icon](elementicons/prepare.png) &nbsp; &nbsp; Prepare {#Prepare}
Produce a prepare file at runtime by connecting instrumentation lines
to outputs.


## Arrays, Matrices and Vectors

### General Array Operators

#### ![icon](elementicons/a-constmultiplier.png) &nbsp; &nbsp; Array Scalar Multiplication {#Array_scalar_multiplication}
Multiplies an array by a scalar (constant) - gives another array of the same dimensionality.

#### ![icon](elementicons/a-summer.png) &nbsp; &nbsp; Array Addition {#Array_addition}
Addition of two arrays (of same dimensionality) - gives another array of that dimensionality.

#### ![icon](elementicons/a-multiplier.png) &nbsp; &nbsp; Array Multiplication {#Array_multiplication}
Multiplication of 2D array by a 1D or 2D array - gives another array of appropriate dimensionality.

### Matrix Operators

#### ![icon](elementicons/m-inverse.png) &nbsp; &nbsp; Matrix Inverse {#Matrix_inverse}
Inverse of a square matrix (Real(*,*) - f := INV(x) - gives another matrix of the same dimensionality.

#### ![icon](elementicons/m-transpose.png) &nbsp; &nbsp; Matrix Transpose {#Matrix_transpose}
Transpose of a matrix (Real(*,*) - f := TRNSP(x) - gives another matrix of appropriate dimensionality.

#### ![icon](elementicons/m-determinant.png) &nbsp; &nbsp; Matrix Determinant {#Matrix_determinant}
Determinant of a square matrix (Real(*,*) - f := DET(x) - gives a scalar).

### Vector Operators

#### ![icon](elementicons/v-merge.png) &nbsp; &nbsp; Vector Merge {#Vector_Merge}
Merges 3 real inputs to a vector output.

#### ![icon](elementicons/v-split.png) &nbsp; &nbsp; Vector Split {#Vector_Split}
Splits a vector input to 3 real outputs.

#### ![icon](elementicons/v-dot.png) &nbsp; &nbsp; Vector Dot Product {#Vector_dot_product}
Dot product of two vectors (Real(3) - z := x.y) - gives a scalar (Real).

#### ![icon](elementicons/v-cross.png) &nbsp; &nbsp; Vector Cross Product {#Vector_cross_product}
Cross product of two vectors (Real(3) - f := x^y) - gives another vector).

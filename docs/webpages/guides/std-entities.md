Standard Simulation Entities
============================

In ESL-Studio, simulation entities are represented by graphical objects
(icons) that may be placed on a simulation block diagram and may be
connected up with signal lines.

These are available from the Elements pane, in the form of a classified
tree view.

This help page covers the standard set of simulation entities provided
in ESL-Studio (in alphabetical order).

### Absolute {#Absolute}
Absolute value of input. This is the modelling version of the standard
function which treats changes in output as discontinuities (uses
Library submodel ABSX).

### Arc Cosine {#Arc_Cosine}
Arc-cosine of input.

### Arc Sine {#Arc_Sine}
Arcsine of input.

### Arc Tangent {#Arc_Tangent}
Arctangent of input.

### Arc Tangent 2 {#Arc_Tangent_2}
Arctangent of two inputs (x / y).

### Backlash {#Backlash}
Comparator with backlash - logical output becomes TRUE when input x
greater than or equal to upper limit and FALSE when less than lower
limit (uses Library submodel COMPB).

### Base 10 Logarithm {#Base_10_Logarithm}
Logarithm to base 10 of input.

### Bistable {#Bistable}
Bistable storage device - stores logical input as the clock input
becomes TRUE (uses Library submodel BISTBL).

### Comparator {#Comparator}
Logical output true if inputs (x >= y).

### Complex Pole {#Complex_Pole}
Second order lag (uses Library submodel CMPXPL).

### Constant False {#Constant_False}
LOGICAL constant with value FALSE.

### Constant Integer {#Constant_Integer}
INTEGER constant value.

### Constant Logical {#Constant_Logical}
LOGICAL constant value determined by attribute.

### Constant Multiplier {#Constant_Multiplier}
Multiplies input by a constant (y = K * x).

### Constant Real {#Constant_Real}
REAL constant value.

### Constant True {#Constant_True}
LOGICAL constant with value TRUE.

### Cosine {#Cosine}
Cosine of input in radians.

### Deadspace {#Deadspace}
Simulates the effect of a 'deadspace'. Output y = 0.0, if LL &lt; x
&lt; UL; y = x-UL, if x >= UL; y = x-LL, if x &lt;= LL (uses Library
submodel DEADSP).

### Delay {#Delay}
Periodically samples a continuous input signal and delays output of the
sampled signal for a fixed period of time, for example a pipeline delay
(uses Library submodel DELAY).

### Derivative {#Derivative}
First-order derivative (uses Library submodel DERIV).

### Divider {#Divider}
Quotient of signed inputs (x / y).

### Exponential {#Exponential}
Exponential of input (e ** x).

### First Order Hold {#First_Order_Hold}
Periodically samples a continuous input signal and produces an output
of the last sample modified with a slope calculated by the previous two
samples (uses Library submodel FHOLD).

### Fourier Transform {#Fourier_Transform}
Fourier integrator - Calculates the rms magnitude and angle of a
specified harmonic component of the Fourier series for an input signal.
Prints stats at the end of each cycle (uses Library submodel FOURINT).

### Friction {#Friction}
Determines the friction between sliding surfaces from applied force and
relative velocity (uses Library submodel COULOMB).

### Function Generator {#Function_Generator}
Generates function values from a one-, two- or three- dimension table
(uses Library submodel FG3D).

### Hysteresis {#Hysteresis}
Implements a pure hysteresis or backlash function (uses Library
submodel HSTRSS).

### Impulse Input {#Impulse_Input}
Generates a periodic train of impulses with a controlled delay before
the first pulse (uses Library submodel IMPUL).

### Integer {#Integer}
Output is the integer value of real input. This is the modelling
version of the standard function which treats changes in output as
discontinuities (uses Library submodel INTX).

### Integer Input {#Integer_Input}
INTEGER input argument to a submodel.

### Integer Output {#Integer_Output}
INTEGER output argument from a submodel.

### Integrator {#Integrator}
Integral of input with respect to time.

### Lead Lag {#Lead_Lag}
Lead-lag transfer function (uses Library submodel LEDLAG).

### Limited Integrator {#Limited_Integrator}
Integrator in which output is bounded between lower and upper limits
(uses Library submodel LIMINT).

### Limiter {#Limiter}
The output follows the input provided the input remains between lower
and upper limits. The output is held at a limit if the input goes
outside the limits (uses Library submodel LIMIT).

### Logical And {#Logical_And}
Logical AND (conjunction) of two inputs.

### Logical Input {#Logical_Input}
LOGICAL input argument to a submodel.

### Logical Integrator {#Logical_Integrator}
Logically controlled integrator - the integrator's mode of operation is
controlled by logical input signals (uses Library submodel LOGINT).

### Logical Negation {#Logical_Negation}
Logical NOT (negation) of input.

### Logical Or {#Logical_Or}
Logical OR (disjunction) of two inputs.

### Logical Output {#Logical_Output}
LOGICAL output argument from a submodel.

### Modulator {#Modulator}
Pulse width modulator - generates a periodic logical pulse train with
the mark/space ratio being controlled by an input variable and an
optional time delay before the first transition (uses Library submodel
MODULT).

### Monostable {#Monostable}
Output set TRUE when input becomes positive and remains set for at
least a time period specified by attribute, or until the input variable
becomes negative (uses Library submodel MONO).

### Multiplier {#Multiplier}
Product of signed inputs (x * y).

### Natural Logarithm {#Natural_Logarithm}
Natural logarithm of input.

### PI Controller {#PI_Controller}
Proportional plus integral (PI) controller (uses Library submodel
PICONT).

### PID Controller {#PID_Controller}
Three term (PID) controller with limited output and integral
anti-windup (uses Library submodel PIDCONT).

### PID Controller 1 {#PID_Controller_1}
Three term (PID) controller with limited output, anti-windup and
deadspace (uses Library submodel PIDCONT1).

### Plot (Display Icon) {#Plot}
Display a runtime plot by connecting instrumentation lines to outputs.

### Power {#Power}
Raises first input to value of second input (exponentiation) (x ** y).

### Prepare (Display Icon) {#Prepare}
Produce a prepare file at runtime by connecting instrumentation lines
to outputs.

### Pulse Input {#Pulse_Input}
Generates a unit pulse of specified duration (uses Library submodel PULSE).

### Quantizer {#Quantizer}
Quantizes a continuous input signal into values which are integer
multiples of a specified quantization value (uses Library submodel
QNTZR).

### Ramp Input {#Ramp_Input}
Generates a ramp of unit slope after optional initial time delay (uses
Library submodel RAMP).

### Real Input {#Real_Input}
REAL input argument to a submodel.

### Real Output {#Real_Output}
REAL output argument from a submodel.

### Real Pole {#Real_Pole}
First order lag (uses Library submodel REALPL).

### Rectifier {#Rectifier}
The operation of a Silicon Controlled Rectifier (SCR) is represented
for given inputs of current, voltage and gate pulse (uses Library
submodel RECT).

### Sample and Hold {#Sample_and_Hold}
Periodically samples a continuous input signal and outputs the value at
the last sampling point (uses Library submodel SAMHLD).

### Sine {#Sine}
Sine of input in radians.

### Sine Input {#Sine_Input}
Generates a sine wave of specified amplitude, frequency, and phase.

### Square Input {#Square_Input}
Generates a square wave of specified amplitude, M/S ratio, period, and
initial time-delay (includes Library submodel MODULT).

### Square Root {#Square_Root}
Square root of absolute value of real input (uses Library submodel
SQRTX).

### Standard Integrator {#Standard_Integrator}
Integral of input with respect to time.

### Step Input {#Step_Input}
Generates a step function (includes Library submodel STEPP).

### Submodel Call {#Submodel_Call}
Calls a submodel.

### Summer {#Summer}
Sum of two signed inputs (x + y).

### Summer 3 {#Summer_3}
Sum of three signed inputs (x + y + z).

### Switch {#Switch}
Switch between two REAL inputs depending on LOGICAL control input.

### Table (Display Icon) {#Table}
Display a runtime table by connecting instrumentation lines to outputs.

### Tangent {#Tangent}
Tangent of input in radians.

### Time Input {#Time_Input}
Simulation time (T).

### Timer {#Timer}
Measures the simulation time which has elapsed since it was reset by a
logical input (uses Library submodel TIMER).

### Transfer Function {#Transfer_Function}
Specifies a Laplace Transfer Function (generates an ESL TRANSFER
statement).

### Zero Order Hold {#Zero_Order_Hold}
Output holds value of x input when hold input becomes TRUE. While hold
is FALSE output is equal to input (uses Library submodel ZHOLD).

EC-LAB SETTING FILE

Number of linked techniques : 5

EC-LAB for windows v11.43 (software)
Internet server v11.40 (firmware)
Command interpretor v11.43 (firmware)

Filename : S:\ec-lab\data\RoKIT\multi_technique\multi_technique_to_ti.mps

Device : SP-300
Electrode connection : standard
Potential control : Ewe
Ewe ctrl range : min = -2.50 V, max = 2.50 V
Ewe,I filtering : 50 kHz
Safety Limits :
	Do not start on E overload
Channel : Grounded
Electrode material : 
Initial state : 
Electrolyte : 
Comments : 
Cable : standard
Electrode surface area : 0.000 cm²
Characteristic mass : 0.001 g
Equivalent Weight : 0.000 g/eq.
Density : 0.000 g/cm3
Volume (V) : 0.001 cm³
Cycle Definition : Charge/Discharge alternance
Do not turn to OCV between techniques

Technique : 1
Trigger In
Trigger             Rising Edge         
Channel             -1                  

Technique : 2
Cyclic Voltammetry
Ei (V)              0.000               
vs.                 Eoc                 
dE/dt               20.000              
dE/dt unit          mV/s                
E1 (V)              0.100               
vs.                 Ref                 
Step percent        50                  
N                   10                  
E range min (V)     -2.500              
E range max (V)     2.500               
I Range             Auto                
I Range min         Unset               
I Range max         Unset               
I Range init        Unset               
Bandwidth           8                   
E2 (V)              -0.100              
vs.                 Ref                 
nc cycles           0                   
Reverse Scan        1                   
Ef (V)              0.000               
vs.                 Eoc                 

Technique : 3
Chronoamperometry / Chronocoulometry
Ei (V)              0.350               
vs.                 Ref                 
ti (h:m:s)          0:00:10.0000        
Imax                pass                
unit Imax           mA                  
Imin                pass                
unit Imin           mA                  
dQM                 0.000               
unit dQM            mA.h                
record              <I>                 
dI                  5.000               
unit dI             µA                  
dQ                  0.000               
unit dQ             mA.h                
dt (s)              0.1000              
dta (s)             0.1000              
E range min (V)     -2.500              
E range max (V)     2.500               
I Range             Auto                
I Range min         Unset               
I Range max         Unset               
I Range init        Unset               
Bandwidth           8                   
goto Ns'            0                   
nc cycles           0                   

Technique : 4
Open Circuit Voltage
tR (h:m:s)          0:00:5.0000         
dER/dt (mV/h)       1.0                 
record              <Ewe>               
dER (mV)            0.00                
dtR (s)             0.5000              
E range min (V)     -2.500              
E range max (V)     2.500               

Technique : 5
Trigger Out
Trigger             Rising Edge         
td (h:m:s)          0:00:0.0010         

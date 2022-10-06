EC-LAB SETTING FILE

Number of linked techniques : 3

EC-LAB for windows v11.43 (software)
Internet server v11.40 (firmware)
Command interpretor v11.43 (firmware)

Filename : S:\ec-lab\data\test\another_ti_ocv_to.mps

Device : SP-300
Electrode connection : standard
Potential control : Ewe
Ewe ctrl range : min = -10.00 V, max = 10.00 V
Ewe,I filtering : 50 kHz
Channel : Grounded
Electrode material : 
Initial state : 
Electrolyte : 
Comments : 
Cable : standard
Electrode surface area : 0.000 cm²
Characteristic mass : 0.001 g
Volume (V) : 0.001 cm³
Thickness (t) : 0.000 cm
Diameter (d) : 0.000 cm
Cell constant (k=t/A) : 0.000 cm-1
Cycle Definition : Charge/Discharge alternance
Turn to OCV between techniques

Technique : 1
Trigger In
Trigger             Rising Edge         
Channel             -1                  

Technique : 2
Open Circuit Voltage
tR (h:m:s)          0:00:5.0000         
dER/dt (mV/h)       1.0                 
record              <Ewe>               
dER (mV)            0.00                
dtR (s)             0.5000              
E range min (V)     -10.000             
E range max (V)     10.000              

Technique : 3
Trigger Out
Trigger             Rising Edge         
td (h:m:s)          0:00:0.0010         

from ophyd import EpicsSignal, EpicsSignalRO, Device
from ophyd import Component as Cpt

# Exposes functionality of the mostab https://gitlab.helmholtz-berlin.de/sissy/support/mostab Which is used by the DCM

# Assumes that the mostab is connected to some sort of beam diagnostic like a mirror current.

class Mostab(Device):
    
    #Define the signals in our component
    setpoint    =  Cpt(EpicsSignal, 'rbkSetpoint',      write_pv = 'setSetpoint',   kind='config')
    gain        =  Cpt(EpicsSignal, 'rbkGain',          write_pv = 'setGain',       kind='config')
    integral    =  Cpt(EpicsSignal, 'rbkIntegral',      write_pv = 'setIntegral',   kind='config')
    derivative  =  Cpt(EpicsSignal, 'rbkDerivative',    write_pv = 'setDerivative', kind='config')
    low_pass    =  Cpt(EpicsSignal, 'rbkLowpass',       write_pv = 'setLowpass',    kind='config')
    
    #Output
    output      =  Cpt(EpicsSignal, 'rbkOutput',        write_pv = 'setOutput',     kind='hinted', labels={"motors", "mostab"})    # Output can only be set if in manual mode
    
    
    #Mode Settings
    status                  = Cpt(EpicsSignalRO,  'rdStatus',        string='True', kind='hinted')
    manual_mode_cmd         = Cpt(EpicsSignal,    'cmdManualMode',                  kind='config')    # turns the mostab feedback "off"
    auto_mode_cmd           = Cpt(EpicsSignal,    'cmdAutoMode',                    kind='config')
    peak_search_mode_cmd    = Cpt(EpicsSignal,    'cmdPeakSearchMode',              kind='config')
    track_setpoint_mode_cmd = Cpt(EpicsSignal,    'cmdPeakSearchMode',              kind='config')
    peak_hold_mode_cmd      = Cpt(EpicsSignal,    'cmdPeakHoldMode',                kind='config')    # turns the mostab feedback "on"  

    
        
       
   

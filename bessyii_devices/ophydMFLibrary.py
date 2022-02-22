from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device
from ophyd import Component as Cpt
from ophyd import status, DeviceStatus, Signal
from ophyd.status import SubscriptionStatus, MoveStatus, AndStatus 
import time
from types import SimpleNamespace
# Define a new kind of device.
"""
if
class monoDummy(PVPositioner):
    setpoint = Cpt(EpicsSignal, 'Mono-SP')
    readback = Cpt(EpicsSignalRO, 'Mono-RB')
    done = Cpt(EpicsSignalRO, 'MonoDone-I')
    
    
class mono(PVPositioner):
    setpoint        = Cpt(EpicsSignal,      'monoSetEnergy'              )
    readback        = Cpt(EpicsSignalRO,    'monoGetEnergy',kind='hinted') # the main output
    done            = Cpt(EpicsSignalRO,    'GK_STATUS'                  )
    
    #configuration
    grating         = Cpt(EpicsSignalRO,    'lineDensity',  kind='config') 
    cff             = Cpt(EpicsSignalRO,    'c',            kind='config')
    exit_slit_size  = Cpt(EpicsSignalRO,    'slitwidth',    kind='config')
fi
"""
 


"""
if
class keithley6514(Device):

    
    init_cmd            = Cpt(EpicsSignal,  'cmdStart')
    trigger_cmd         = Cpt(EpicsSignal,  'rdCur.PROC')
    readback            = Cpt(EpicsSignalRO,'rdCur',      kind='hinted')
    zero_check  		= Cpt(EpicsSignal,  'cmdZeroCheck',        kind='config')
    
    mode    		= Cpt(EpicsSignal,  'setFunc',        kind='config')
    reset               = Cpt(EpicsSignal,  'cmdReset.PROC',        kind='config')

    #configuration
    range               = Cpt(EpicsSignal,  'setRangeCur',        kind='config')
    scan                = Cpt(EpicsSignal,  'rdCur.SCAN',kind='config')
    nplc                = Cpt(EpicsSignal,  'setIntegrTime',         kind='config') #Number of power line cycles
    navg                = Cpt(EpicsSignal,  'setFiltAverCnt',         kind='config')
    filter		= Cpt(EpicsSignal,  'cmdFiltAverEnable', kind='config')
 
    # missing trig source

    def stage(self):
        
        #self.reset_cmd.put(1)           # put rather than set due to weird support module, so reutrns no status
        self.scan.put('Passive')

        self.zero_check.put(0)
        self.mode.put('Current')
        self.init_cmd.put(1)

        #self.trigger_cmd.put(1)
        #self.fetch_cmd.put(1)
        time.sleep(3) #incase zero check has changed
        #Change to passive polling
        super().stage()

    def unstage(self):
        
        #self.scan.put('Passive')
        #self.mode.put(1) #standard current measurement
        
        
        super().unstage()  

    def trigger(self):
           
        #Create a callback called if count is processed
        def new_value(*,old_value,value,**kwargs):

            status.set_finished()
            
            # Clear the subscription.
            self.readback.clear_sub(new_value)

        #Create the status object
        status = DeviceStatus(self.readback,timeout = 10.0)

        #Connect the callback that will set finished and clear sub
        self.readback.subscribe(new_value,event_type=Signal.SUB_VALUE,run=False)
        
        #Start the acquisition
        self.trigger_cmd.put(1)
        
                
        
        return status
fi
"""


class keithley6485(Device):

    
    init_cmd            = Cpt(EpicsSignal,  'sdc')
    trigger_cmd         = Cpt(EpicsSignal,  '.PROC')
    readback            = Cpt(EpicsSignalRO,'rawData',      kind='hinted')
    zero_check 		= Cpt(EpicsSignal,  'zeroChk',        kind='config')
    
    #mode    		= Cpt(EpicsSignal,  'setFunc',          kind='config')
    reset               = Cpt(EpicsSignal,  'sdc',       	kind='config')

    #configuration
    range               = Cpt(EpicsSignal,  'range',        	kind='config')
    scan                = Cpt(EpicsSignal,  'rawData.SCAN',	kind='config')
    nplc                = Cpt(EpicsSignal,  'intTime',          kind='config') #Number of power line cycles
    navg                = Cpt(EpicsSignal,  'averFltCount',     kind='config')
    filter		= Cpt(EpicsSignal,  'averFlt', 		kind='config')
 
    # missing trig source

    def stage(self):
        
        #self.reset_cmd.put(1)           # put rather than set due to weird support module, so reutrns no status
        #self.scan.put('Passive')
        self.scan.put('6')

        self.zero_check.put(0)
        #self.mode.put('Current')
        self.init_cmd.put(1)

        #self.trigger_cmd.put(1)
        #self.fetch_cmd.put(1)
        time.sleep(3) #incase zero check has changed
        #Change to passive polling
        super().stage()

    def unstage(self):
        
        #self.scan.put('Passive')
        #self.mode.put(1) #standard current measurement
        
        
        super().unstage()  

    def trigger(self):
           
        #Create a callback called if count is processed
        def new_value(*,old_value,value,**kwargs):

            status.set_finished()
            
            # Clear the subscription.
            self.readback.clear_sub(new_value)

        #Create the status object
        status = DeviceStatus(self.readback,timeout = 10.0)

        #Connect the callback that will set finished and clear sub
        self.readback.subscribe(new_value,event_type=Signal.SUB_VALUE,run=False)
        
        #Start the acquisition
        self.trigger_cmd.put(1)
        
                
        
        return status




"""
if
class channeltronDummy(Device):
    
    #Define the signals in our component
    
    read_cmd    = Cpt(EpicsSignal, 'DummyStart-CMD')         # Starts a read
    count       = Cpt(EpicsSignalRO, 'DummyCounter-RB', kind='hinted') # hinted makes it show up in visualisations.
    interval    = Cpt(EpicsSignal, 'Interval-SP', kind='config')
    threshold   = Cpt(EpicsSignal, 'Threshold-SP', kind='config')
    highVoltage = Cpt(EpicsSignal, 'HighVoltage-SP', kind='config')
    deadTime    = Cpt(EpicsSignal, 'DeadTime-SP', kind='config')

    def stage(self):
        #Set High Voltage, wait for it to reach correct value
        super().stage()

    def unstage(self):
        # Turn high voltage off
        super().unstage()    
    
    
    def trigger(self):
    
        #Create a callback called if count is processed
        def new_value(*,old_value,value,**kwargs):

            status.set_finished()
            
            # Clear the subscription.
            self.count.clear_sub(new_value)

        #Create the status object
        status = DeviceStatus(self.count,timeout = 10.0)

        #Connect the callback that will set finished and clear sub
        self.count.subscribe(new_value,event_type=Signal.SUB_VALUE,run=False)
        
        #Start the acquisition
        self.read_cmd.set(1)

        
        return status
fi
"""

"""
if
class channeltron(Device):
    
    #Define the signals in our component
    
    read_cmd    = Cpt(EpicsSignal, 'Start-CMD')         # Starts a read
    count       = Cpt(EpicsSignalRO, 'Counter-RB', kind='hinted') # hinted makes it show up in visualisations.
    duration    = Cpt(EpicsSignal, 'Interval-SP')

    interval    = Cpt(EpicsSignal, 'Interval-SP', kind='config')
    threshold   = Cpt(EpicsSignal, 'Threshold-SP', kind='config')
    highVoltage = Cpt(EpicsSignal, 'HighVoltage-SP', kind='config')
    deadTime    = Cpt(EpicsSignal, 'DeadTime-SP', kind='config')
    
    
    
    def trigger(self):
    
        #variable used as an event flag
        acquisition_status = False
           
        def acquisition_started():
            nonlocal acquisition_status #Define as nonlocal as we want to modify it
            acquisition_status = True
                
        def check_value(*, old_value, value, **kwargs):
            #Return True when the acquisition is complete, False otherwise.
                                   
            if not acquisition_status:  #But only report done if acquisition was already started
                
                return False
                       
            return (old_value != value)
        
        # create the status with SubscriptionStatus that add's a callback to check_value.
        # timeout is set at 1 second + whatever the duration is in ms
        sta_cnt = SubscriptionStatus(self.count, check_value, timeout=10.0, run=False)
         
        # Start the acquisition
        sta_acq = self.read_cmd.set(1)
        
        sta_acq.add_callback(acquisition_started)
        
        stat = AndStatus(sta_cnt, sta_acq)
        
        return stat
fi
"""

def hw(save_path=None):

    "Test hardware to call"
    #sys = 'SISSY2EX:' 
    ks = 'K64851MF102L:' 

    #emil_dummy_chan = channeltronDummy(sys + 'Channeltron0:', name='emil_dummy_chan', read_attrs=['count'],configuration_attrs=['interval','deadTime','highVoltage', 'threshold'])
    #emil_dummy_mono = monoDummy(sys + 'Channeltron0:', name='emil_dummy_mono', read_attrs=['readback'])
    #sissy2_chan0        = channeltron(sys + 'Channeltron0:', name='sissy2_chan', read_attrs=['count'],configuration_attrs=['interval','deadTime','highVoltage', 'threshold'])
    #sissy2_keithley0    = keithley6514(sys + 'Keithley0:', name='sissy2_keithley0', read_attrs=['readback'])
    
    #u171_mono = mono('u171dcm1:', name='u171_mono', read_attrs=['readback']) 
    #u481_mono = mono('ue481pgm1:', name='u481_mono', read_attrs=['readback'])
    #u481_mono.done_value = 0


    myspot_keithley0    = keithley6485(ks + '12', name='myspot_keithley0', read_attrs=['readback'])
    myspot_keithley1    = keithley6485(ks + '14', name='myspot_keithley1', read_attrs=['readback'])

    # Because some of these reference one another we must define them (above)
    # before we pack them into a namespace (below).
    
    return SimpleNamespace(
    
        #emil_dummy_chan=emil_dummy_chan,
        #emil_dummy_mono=emil_dummy_mono,
        #sissy2_chan0=sissy2_chan0,
        #sissy2_keithley0=sissy2_keithley0,
        #u171_mono=u171_mono,
        #u481_mono=u481_mono,
        myspot_keithley0=myspot_keithley0,
        myspot_keithley1=myspot_keithley1,
        
    )
    
# Dump instances of the example hardware generated by hw() into the nonlocal
# namespcae for convenience and back-compat.
globals().update(hw().__dict__)

#
from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device
from ophyd import Component as Cpt
from ophyd import status, DeviceStatus, Signal
from ophyd.status import SubscriptionStatus, MoveStatus, AndStatus 
import time
from types import SimpleNamespace
 
class Keithley6514(Device):

    def __init__(self, prefix, *args, **kwargs):
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name 
    
    # Ophyd Device for https://gitlab.helmholtz-berlin.de/sissy/support/keithley/-/blob/master/keithleyApp/Db/Keithley6514Main.template
    
    init_cmd            = Cpt(EpicsSignal, 'cmdStart', kind="omitted")
    abort               = Cpt(EpicsSignal, 'cmdCancel', kind="omitted")
    trigger_cmd         = Cpt(EpicsSignal, 'rdCur.PROC', kind="omitted")
    readback            = Cpt(EpicsSignalRO, 'rdCur', kind='hinted', labels={"detectors", "keithley"})
    zero_check  		= Cpt(EpicsSignal, 'cmdZeroCheck', kind='config')
    mdel                = Cpt(EpicsSignal, 'rdCur.MDEL', kind='config')
    
    func    		    = Cpt(EpicsSignal, 'rbkFunc', write_pv='setFunc', string='True', kind='config')

    reset               = Cpt(EpicsSignal, 'cmdReset.PROC', kind='config')
    scan                = Cpt(EpicsSignal, 'fwdMeas.SCAN',string='True', kind='config')                               #the rate at which the PV will update.
    
    ## -----  configuration ------
    
    # range
    rnge                = Cpt(EpicsSignal, 'rbkRangeCur', write_pv='setRangeCur', string='True', kind='config')
    auto_rnge           = Cpt(EpicsSignal, 'rbkRangeCurAuto', string='True', kind='config')
    auto_rnge_llim      = Cpt(EpicsSignal, 'setRangeCurAutoLLIM', kind='config')
    auto_rnge_ulim      = Cpt(EpicsSignal, 'setRangeCurAutoULIM', kind='config')
    
    # integration time
    nplc                = Cpt(EpicsSignal, 'rbkIntegrTime',write_pv = 'setIntegrTime', kind='config') #Number of power line cycles
    #int_time            = Cpt(EpicsSignal, 'rbkIntegrTimeSec',write_pv = 'setIntegrTimeSec', kind='config') 
    #Damping            
    analog_dmp_ena      = Cpt(EpicsSignal, 'rbkFiltDampEnable', write_pv='cmdFiltDampEnable', kind='config')
    
    # median filter
    medn_filt_rank      = Cpt(EpicsSignal, 'rbkFiltMedRnk', write_pv='setFiltMedRnk', kind='config') #set Rank, sample Readings = (2 x R) + 1
    medn_filt_ena       = Cpt(EpicsSignal, 'rbkFiltMedEnable', write_pv='cmdFiltMedEnable', kind='config')
    
    # averaging filter
    avg_num             = Cpt(EpicsSignal, 'rbkFiltAverCnt', write_pv='setFiltAverCnt', kind='config') 
    avg_type            = Cpt(EpicsSignal, 'rbkFiltAverCtrl', write_pv='cmdFiltAverCtrl', string='True', kind='config')  # "Moving" or "Repeat", readback is "MOV" or "REP"
    
    # arming and triggering
    arm_src             = Cpt(EpicsSignal, 'rbkArmSrc', write_pv='setArmSrc', string='True', kind='config')  # default to immediate
    trig_src            = Cpt(EpicsSignal, 'rbkTrgSrc', write_pv='setTrgSrc',  string='True', kind='config')  # default to immediate (Otherwise "Trigger Link")
    trig_line           = Cpt(EpicsSignal, 'rbkTrgInLine', write_pv='setTrgInLine' , kind='config')  # which trigger line [1:6] to use if trig_src is set to 1, "Trigger Link"
    trig_delay          = Cpt(EpicsSignal, 'rbkTrgDly', write_pv='setTrgDly' , kind='config')
    
    # front panel
    front_panel         = Cpt(EpicsSignal, 'rbkDisp', write_pv='cmdDisp',string='True', kind='config')  # default to "On"
 
    def stage(self):

        self.scan.put('Passive')      # update the EPICS PV as quick as we can, modified 2.03.2022 to not shift values
        self.front_panel.put('On')      # Turn the front panel on (might be bad for readback)
        self.avg_type.put('Moving')     # Moving average filter, for speed of readback
        self.arm_src.put('Immediate')   # Immediate arm to give the fastest update possible
        self.trig_src.put('Immediate')  # Immediate trigger to give the fastest update possible


        # deal with zero_check
        if self.zero_check.get() == 1 :
            
            self.zero_check.put(0)
            time.sleep(10) 
        
        self.func.put('Current')        # Make sure we are in current mode
        
        self.init_cmd.put(1)            # start the aquisition if it isn't already

        self.mdel.put(-1)
        super().stage()

    def unstage(self):
        self.scan.put('.1 second')
        super().unstage()  
     

    def trigger(self):
           
        #Create a callback called if count is processed
        def new_value(*,old_value,value,**kwargs):          #MDEL of $(P):rdCur must be set to -1

            status.set_finished()
            
            # Clear the subscription.
            self.readback.clear_sub(new_value)

        #Create the status object
        status = DeviceStatus(self.readback,timeout = 10.0)

        #Connect the callback that will set finished and clear sub
        self.readback.subscribe(new_value,event_type=Signal.SUB_VALUE,run=False)
        

        self.trigger_cmd.put(1)     # will have started anyway since we set scan to .1 second
        
        return status


class Keithley6517(Keithley6514):

       
    vsrc_ena            = Cpt(EpicsSignal, 'cmdVoltSrcEna', kind="omitted")
    vsrc                = Cpt(EpicsSignal, 'rbkVoltSrc' , write_pv='setVoltSrc',       kind='config')
    acq_mode    		= Cpt(EpicsSignal, 'rbkTrigCont', write_pv='setTrigCont',        string='True',      kind='config')    #single or continuous mode. Bypasses event detection (trig_src)

    def unstage(self):
        self.acq_mode.put("Continuous")
        super().unstage()  

class Keithley6517Old(Keithley6514):


    vsrc_ena            = Cpt(EpicsSignal, 'cmdVoltSrcEna', kind="omitted")
    vsrc                = Cpt(EpicsSignal, 'rbkVoltSrc' , write_pv='setVoltSrc',       kind='config')
    #trig_mode                   = Cpt(EpicsSignal, 'rbkTrigCont', write_pv='setTrigCont',        string='True',      kind='config')    #single or continuous mode. Bypasses event detectio>

    #def unstage(self):
    #    self.trig_mode.put("Continuous")
    #    super().unstage()  


class KeysightB2985A(Keithley6514):

       
    
    def stage(self):

        self.scan.put('Passive')      # update the EPICS PV as quick as we can, modified 2.03.2022 to not shift values
       
        # deal with zero_check
        if self.zero_check.get() == 1 :
            
            self.zero_check.put(0)
            time.sleep(10) 
        
        self.mdel.put(-1)
        super().stage()

    def unstage(self):
        self.scan.put('.1 second')
        super().unstage()  

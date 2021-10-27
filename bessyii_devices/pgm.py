from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device
from ophyd.status import DeviceStatus, StatusBase, SubscriptionStatus
import time
from ophyd.status import wait
from ophyd import Component as Cpt


from .flyer import BasicFlyer

from ophyd import FormattedComponent as FCpt
from .positioners import PVPositionerComparator

# Note that changing the grating translation DOES NOT change the MONO calculation parameters
class PGMTranslationAxis(PVPositionerComparator):

    setpoint = FCpt(EpicsSignal,'{self.prefix}PH_{self._ch_num}_SET')
    readback = FCpt(EpicsSignalRO,'{self.prefix}PH_{self._ch_num}_GET')

    #Can't make this one signal because one half is a string
    select    = FCpt(EpicsSignal, '{self.prefix}PH_{self._ch_num}_GON', kind='config')
    selected  = FCpt(EpicsSignal, '{self.prefix}PH_{self._ch_num}_GETN', string='True', kind='hinted')
    relative  = FCpt(EpicsSignal, '{self.prefix}PH_{self._ch_num}_SETSTEP')
    jog       = FCpt(EpicsSignal, '{self.prefix}PH_{self._ch_num}_SETJOGSPEED')

    atol = 0.1  # tolerance before we set done to be 1 (in um) we should check what this should be!

    def done_comparator(self, readback, setpoint):
        return setpoint-self.atol < readback < setpoint+self.atol
        
        
    def __init__(self, prefix, ch_num=None, **kwargs):
        self._ch_num = ch_num
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name

class PGMScannableAxis(PVPositionerComparator):

    setpoint = FCpt(EpicsSignal,'{self.prefix}Set{self._ch_name}')
    readback = FCpt(EpicsSignalRO,'{self.prefix}{self._ch_name}')

      # tolerance before we set done to be 1 (in um) we should check what this should be!

    def done_comparator(self, readback, setpoint):
        return setpoint-self.atol < readback < setpoint+self.atol


    def __init__(self, prefix, ch_name=None,atol=0.01, **kwargs):
        self._ch_name = ch_name
        self.atol = atol
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name




"""
for notes on multiple inheritance see https://stackoverflow.com/a/3277407/14795659 
class Third(First, Second):
    ...

The class below says Python will start by looking at BasicFlyer Class first, and, if BasicFlyer doesn't have the attribute, then it will look at PVPositioner.
"""

"""
:MonoAktion.PROC
    Command Code    Comment
===============================================================================
0               Stop all motors
1               Save monochromator configuration to file (MONO.CFG)
2               Go to zero order
3               Save as zero order (B. Zader Knopf)
5               Zero order step move up
6               Zero order step move down
10              Clear errors on blue panel
20              Sweep init
21              Sweep run
37              Use current position for zero order correction of grating offset.
60              Move to last energy.

:GetSweepState
value   description
==========================
0x02    Go to start of acceleration ramp    
0x04    Ready   -  Standing at the beginning of the ramp, Ready to start
0x20    Started  - Started and on the way to startenergy
0x40    Sweeping  - Running within start- and endenergy    
0xFF    Ready  -   Finished or error.

"""
class PGM(BasicFlyer, PVPositioner):


    def __init__(self, prefix, *args, **kwargs):
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name 

    setpoint            = Cpt(EpicsSignal,      'monoSetEnergy'                                      )
    readback            = Cpt(EpicsSignalRO,    'monoGetEnergy', labels={"motors"},     kind='hinted') # the main output
    done                = Cpt(EpicsSignalRO,    'GK_STATUS'                                          )
    

    #status is an mbbo record, I need to know what the different states are. 
    sweep_status = Cpt(EpicsSignalRO, 'GetSweepState')
    aktion = Cpt(EpicsSignal, 'MonoAktion.PROC') # writing different values to this pv causes different actions like init, start, stop
    start_pos = Cpt(EpicsSignal, 'SetSweepStart'   , kind='config')
    end_pos = Cpt(EpicsSignal, 'SetSweepEnd'   , kind='config')
    velocity = Cpt(EpicsSignal, 'SetSweepVel', kind='config')
  

    # status
    
    cff             = Cpt(EpicsSignal, 'cff', write_pv='SetCff', kind='config')
    diff_order      = Cpt(EpicsSignal, 'Order',write_pv='SetOrder', kind='config')
    grating_no      = Cpt(EpicsSignal, 'SetGratingNo', string='True',kind='config')
    grating         = Cpt(EpicsSignalRO, 'lineDensity', kind='hinted') 
    slitwidth       = Cpt(EpicsSignal,  'slitwidth', write_pv = 'SlitInput',     kind='config')
    
    ID_on           = Cpt(EpicsSignal, 'SetIdOn', string='True',kind='config')
    mode            = Cpt(EpicsSignal, 'GetFormulaMode', write_pv = 'SetFormulaMode', string='True',kind='config') 
    table           = Cpt(EpicsSignal, 'idMbboIndex', string='True',kind='config') 
    table_filename  = Cpt(EpicsSignalRO, 'idFilename', string='True',kind='config') 
    harmonic        = Cpt(EpicsSignal, 'GetIdHarmonic', write_pv = 'Harmonic', string='True',kind='config')
    eMin_eV         = Cpt(EpicsSignalRO, 'minEnergy', kind='hinted')
    eMax_eV         = Cpt(EpicsSignalRO, 'maxEnergy', kind='hinted')
    positioning     = Cpt(EpicsSignalRO, 'multiaxis:mbbiMoveMode', string='True',kind='hinted')

    m2_translation      = Cpt(PGMTranslationAxis, '', ch_num='0',labels={"motors"},kind='config')
    grating_translation = Cpt(PGMTranslationAxis, '', ch_num='1',labels={"motors"},kind='config')
                                             
    set_branch       = Cpt(EpicsSignal,      'SetBranch',              string='True',kind='config')
    alpha            = Cpt(EpicsSignal, 'Alpha', write_pv='SetAlpha', kind='config')
    beta             = Cpt(PGMScannableAxis, '',  ch_name='Beta',settle_time=5.0,atol=0.02, kind='config')
    theta            = Cpt(PGMScannableAxis, '',  ch_name='Theta',settle_time=5.0,atol=0.02, kind='config')

    def kickoff(self):
        """
        Start this Flyer, return a status object that sets finished once we have started
        """
        self.complete_status = DeviceStatus(self)
        self._acquiring = True
        self.t0 = time.time()

        if self.aktion is not None:
            self.aktion.put(20)     # init
        
        def check_ready(*,old_value, value, **kwargs):
            #Return True when the acquisition is complete, False otherwise.   
            if not self._acquiring:  #But only report done if acquisition was already started 
                return False
            return (value == 4) #Running, Sweeping within start and end energy
        
        def check_started(*,old_value, value, **kwargs):
            #Return True when the acquisition is complete, False otherwise.   
            if not self._acquiring:  #But only report done if acquisition was already started 
                return False
            return (value == 64) #Running, Sweeping within start and end energy

        wait(SubscriptionStatus(self.sweep_status, check_ready))
        
        if self.aktion is not None:
            self.aktion.put(21)

        self.kickoff_status = SubscriptionStatus(self.sweep_status, check_started)

        return self.kickoff_status

    def pause(self):

        self.aktion.put(0) # stop all motors
        sta = DeviceStatus(self)
        sta._finished(success=True)
        return sta

    def resume(self):

        self.aktion.put(21) # not sure if this will work

    def stop(self,*, success=False):

        self.aktion.put(0)

        if self.complete_status != None:
            self.complete_status._finished(success=False)


    def complete(self):
        """
        Wait for flying to be complete, get the status object that will tell us when we are done
        """
        def check_value(*,old_value, value, **kwargs):
            #Return True when the acquisition is complete, False otherwise.   
            if not self._acquiring:  #But only report done if acquisition was already started 
                return False
            return (value == 128)

        self.complete_status = SubscriptionStatus(self.sweep_status,check_value)

        return self.complete_status
       

class PGMSoft(PGM):
    grating_800_temp    = FCpt(EpicsSignalRO,  'MONOY02U112L:Grating1T1', labels={'pgm'})
    grating_400_temp    = FCpt(EpicsSignalRO,  'MONOY02U112L:Grating2T1', labels={'pgm'})
    mirror_temp         = FCpt(EpicsSignalRO,  'MONOY02U112L:MirrorT1', labels={'pgm'})



class PGMHard(PGM):
    grating_800_temp    = FCpt(EpicsSignalRO,  'MONOY01U112L:Grating1T1', labels={'pgm'})
    grating_400_temp    = FCpt(EpicsSignalRO,  'MONOY01U112L:Grating2T1', labels={'pgm'})
    mirror_temp         = FCpt(EpicsSignalRO,  'MONOY01U112L:MirrorT1', labels={'pgm'})

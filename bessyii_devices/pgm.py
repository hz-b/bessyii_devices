from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device
from ophyd.status import DeviceStatus, StatusBase, SubscriptionStatus
import time
from ophyd.status import wait
from ophyd import Component as Cpt


from .flyer import BasicFlyer

from ophyd import FormattedComponent as FCpt
from .positioners import PVPositionerComparator

# Note that changing the grating translation DOES NOT change the MONO calculation parameters
class MonoTranslationAxis(PVPositionerComparator):

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



class PGMScannableAxis(PVPositioner):

    setpoint = FCpt(EpicsSignal,'{self.prefix}Set{self._ch_name}')
    readback = FCpt(EpicsSignalRO,'{self.prefix}{self._ch_name}')
    done     = FCpt(EpicsSignalRO,'{self.prefix}Status')
    
    def __init__(self, prefix, ch_name=None, **kwargs):
        self._ch_name = ch_name
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name



class Energy(PVPositioner):

    """
    Energy is a PVPositioner which also reimplements the get() method
    It is intended that this class is included as a component to monochromators
    
    """

    def __init__(self, prefix, *args, **kwargs):
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name 

    # this is an initial API 
    setpoint        = Cpt(EpicsSignal,      'monoSetEnergy'                                  )
    readback        = Cpt(EpicsSignalRO,    'monoGetEnergy', labels={"pgm"},     kind='hinted') # the main output
    done            = Cpt(EpicsSignalRO,    'IStatus'                                          )
    done_value      = 0
    egu = 'eV'  
    
    # so that you can do for example ue48_pgm.en.get() rather than ue48_pgm.en.readback.get()
    def get(self):
        
        return self.readback.get()


class SoftMonoBase(Device):
    """
    SoftMonoBase is a core class which provides controls which are the same for all 
    standard BESSY soft x-ray monochromator, for both dipole and undulator beamlines.

    Generally all monochromators will have a possibility to:
    * set and read energy, energy ranges and etc
    * read (not always freely choose) c value
    * choose diffration order
    * ....
    """
    en              = Cpt(Energy, '')
    diff_order      = Cpt(EpicsSignal, 'Order',write_pv='SetOrder', kind='config')
    grating_no      = Cpt(EpicsSignal, 'SetGratingNo', string='True',kind='hinted', labels={"pgm"})
    grating         = Cpt(EpicsSignalRO, 'lineDensity', kind='hinted') 

    eMin_eV         = Cpt(EpicsSignalRO, 'minEnergy', kind='hinted')
    eMax_eV         = Cpt(EpicsSignalRO, 'maxEnergy', kind='hinted')



class UndulatorMonoBase(SoftMonoBase):
    """
    UndulatorMonoBase contains all additional signals used for monochromators at undulator beamlines. 
    """

    ID_on           = Cpt(EpicsSignal, 'SetIdOn', string='True',kind='config', labels={"pgm"})
    mode            = Cpt(EpicsSignal, 'GetFormulaMode', write_pv = 'SetFormulaMode', string='True',kind='config') 
    table           = Cpt(EpicsSignal, 'idMbboIndex', string='True',kind='config')
    table_filename  = Cpt(EpicsSignalRO, 'idFilename', string='True',kind='config') 
    harmonic        = Cpt(EpicsSignal, 'GetIdHarmonic', write_pv = 'Harmonic', string='True',kind='config')
    
class ExitSlitBase(Device):
    """
    Base class stub (also standard API for many soft x-ray monos) for monochromator exit slit control

    TODO: some SGMs have also entrance slit - Epics API should be checked before finalizing API on ophyd side
    """
    slitwidth       = Cpt(EpicsSignal,  'slitwidth', write_pv = 'SetSlitWidth',     kind='config')
    # Many monos will allow also set "wish" energy resolution by driving exit slit. This shall be included in this class


class ExitSlitEMIL(ExitSlitBase):
    """
    EMIL specific exit slit implementation. EMIL beamlines uses different PV name for setting the slit
    """
    slitwidth       = Cpt(EpicsSignal,  'slitwidth', write_pv = 'SlitInput',     kind='config')

class PGM(SoftMonoBase):
    """
    PGM is a core class for PGM monochromators
    """

    # PGMs has a full control over cff, so override it here
    cff             = Cpt(EpicsSignal, 'cff', write_pv='SetCff', kind='config')
    
class SGM(SoftMonoBase):
    """
    SGM is a core class for SGM monochromators
    """
    cff             = Cpt(EpicsSignalRO, 'cff', kind='hinted')


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
class FlyingPGM(BasicFlyer, SoftMonoBase):

    #status is an mbbo record, I need to know what the different states are. 
    sweep_status    = Cpt(EpicsSignalRO, 'GetSweepState')
    aktion          = Cpt(EpicsSignal, 'MonoAktion.PROC') # writing different values to this pv causes different actions like init, start, stop
    start_pos       = Cpt(EpicsSignal, 'SetSweepStart'   , kind='config')
    end_pos         = Cpt(EpicsSignal, 'SetSweepEnd'   , kind='config')
    velocity        = Cpt(EpicsSignal, 'SetSweepVel', kind='config')
  
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
       
class PGMEmil(UndulatorMonoBase,PGM,ExitSlitEMIL,FlyingPGM):
    
  
    positioning         = Cpt(EpicsSignal, 'multiaxis:mbbiMoveMode', write_pv='multiaxis:mbboSetMoveMode', string='True',kind='hinted')
    m2_translation      = Cpt(MonoTranslationAxis, '', ch_num='0',labels={"pgm"},kind='config')
    grating_translation = Cpt(MonoTranslationAxis, '', ch_num='1',labels={"pgm"},kind='config')
    set_branch          = Cpt(EpicsSignal,      'SetBranch',              string='True',kind='config')
    alpha               = Cpt(EpicsSignal, 'Alpha', write_pv='SetAlpha', kind='config')
    beta                = Cpt(EpicsSignal, 'Beta',  write_pv='SetBeta', kind='config')
    theta               = Cpt(EpicsSignal, 'Theta', write_pv='SetTheta', kind='config')
    
# the name of these two classe has to be changed to be EMIL specific
class PGMSoft(PGMEmil):
    grating_800_temp    = FCpt(EpicsSignalRO,  'MONOY02U112L:Grating1T1', kind='hinted', labels={'pgm'})
    grating_400_temp    = FCpt(EpicsSignalRO,  'MONOY02U112L:Grating2T1', kind='hinted', labels={'pgm'})
    mirror_temp         = FCpt(EpicsSignalRO,  'MONOY02U112L:MirrorT1',   kind='hinted', labels={'pgm'})



class PGMHard(PGMEmil):
    grating_800_temp    = FCpt(EpicsSignalRO,  'MONOY01U112L:Grating1T1', kind='hinted', labels={'pgm'})
    grating_400_temp    = FCpt(EpicsSignalRO,  'MONOY01U112L:Grating2T1', kind='hinted', labels={'pgm'})
    mirror_temp         = FCpt(EpicsSignalRO,  'MONOY01U112L:MirrorT1',   kind='hinted', labels={'pgm'})
    
    
    
class PGM_Aquarius(UndulatorMonoBase):

    # We want to inherit everything from UnUndulatorMonoBase but rewrite these attributes to add settle time and a new attribute fix_theta
    alpha            = Cpt(PGMScannableAxis, '',  ch_name='Alpha', settle_time=10.0, kind='config')
    beta             = Cpt(PGMScannableAxis, '',  ch_name='Beta',  settle_time=10.0, kind='config')
    theta            = Cpt(PGMScannableAxis, '',  ch_name='Theta', settle_time=10.0, kind='config')
    fix_theta        = Cpt(EpicsSignal,  'FixThetaAngle', write_pv = 'SetFixThetaAng', kind='config')

from ophyd import EpicsSignal, EpicsSignalRO, PositionerBase
from ophyd.status import DeviceStatus, StatusBase, SubscriptionStatus, wait as status_wait
import time
from ophyd.status import wait
from ophyd import Component as Cpt
import threading
import numpy as np
from .flyer import BasicFlyer

from ophyd import FormattedComponent as FCpt
from .positioners import PVPositionerComparator, PVPositionerBessy as PVPositioner
from .device import BESSYDevice as Device

from collections import OrderedDict, namedtuple
from collections.abc import Iterable, MutableSequence
from enum import Enum
from typing import (
    Any,
    Callable,
    ClassVar,
    DefaultDict,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
)

class MonoTranslationAxisSelect(PVPositioner):

    """
    This axis is used for moving things inside the mono. It does not change the calc params. They must be changed seperately
    
    This axis is not intended to be, and cannot be scanned. It's used so that we have a status object to know when the move is complete
    """
    
    def __init__(self, prefix, ch_num=None, **kwargs):
        self._ch_num = ch_num
        super().__init__(prefix, **kwargs)
        
    setpoint = FCpt(EpicsSignal, '{self.prefix}PH_{self._ch_num}_GON', kind='normal')
    readback = FCpt(EpicsSignalRO, '{self.prefix}PH_{self._ch_num}_GETN',string='True', kind='hinted')
    done      = FCpt(EpicsSignal, '{self.prefix}PH_{self._ch_num}_STATUS.RVAL', kind='omitted')
    done_value = 0.0
       
      
        
        
# Note that changing the grating translation DOES NOT change the MONO calculation parameters
class MonoTranslationAxis(PVPositioner):

    def __init__(self, prefix,atol=0, ch_num=None, **kwargs):
        self._ch_num = ch_num
        self._atol = atol
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name
    """
    This axis is used for moving things inside the mono. It does not change the calc params. They must be changed seperate
    """
    setpoint = FCpt(EpicsSignal,'{self.prefix}PH_{self._ch_num}_SET', kind='normal')
    readback = FCpt(EpicsSignalRO,'{self.prefix}PH_{self._ch_num}_GET', kind = 'hinted')
    done      = FCpt(EpicsSignal, '{self.prefix}PH_{self._ch_num}_STATUS', kind='omitted')
    stop_signal= FCpt(EpicsSignal, '{self.prefix}PH_{self._ch_num}_AKTION', kind='omitted')
    stop_value = 0
    done_value = 0

    def move(self, position, wait=True, timeout=None, moved_cb=None):
        """Move to a specified position, optionally waiting for motion to
        complete.
        Parameters
        ----------
        position
            Position to move to
        moved_cb : callable
            Call this callback when movement has finished. This callback must
            accept one keyword argument: 'obj' which will be set to this
            positioner instance.
        timeout : float, optional
            Maximum time to wait for the motion. If None, the default timeout
            for this positioner is used.
        Returns
        -------
        status : MoveStatus
        Raises
        ------
        TimeoutError
            When motion takes longer than `timeout`
        ValueError
            On invalid positions
        RuntimeError
            If motion fails other than timing out
        """
        # Before moving, ensure we can stop (if a stop_signal is configured).
        if self.stop_signal is not None:
            self.stop_signal.wait_for_connection()
        status = PositionerBase.move(self,position, timeout=timeout, moved_cb=moved_cb) #doesn't a

        
                
        has_done = self.done is not None
        if not has_done:
            moving_val = 1 - self.done_value
            self._move_changed(value=self.done_value)
            self._move_changed(value=moving_val)

        try:
            if np.abs(self.readback.get() - position) > self._atol:
                self._setup_move(position)
            else:
                moving_val = 1 - self.done_value
                self._move_changed(value=self.done_value)
                self._move_changed(value=moving_val)
                self._move_changed(value=self.done_value)

                PositionerBase._done_moving(self)
            if wait:
                status_wait(status)
        except KeyboardInterrupt:
            self.stop()
            raise
  
            

        return status






class PGMScannableAxis(PVPositioner):

    setpoint = FCpt(EpicsSignal,'{self.prefix}Set{self._ch_name}', kind='normal')
    readback = FCpt(EpicsSignalRO,'{self.prefix}{self._ch_name}', kind='hinted')
    done     = FCpt(EpicsSignalRO,'{self.prefix}Status', kind='omitted')
    
    def __init__(self, prefix, ch_name=None, **kwargs):
        self._ch_name = ch_name
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name

class MonoComparatorAxis(PVPositionerComparator):

    setpoint    = FCpt(EpicsSignal,    '{self.prefix}Set{self._ch_name}', kind='normal' )
    readback    = FCpt(EpicsSignalRO,  '{self.prefix}{self._ch_name}', kind='hinted')



    def done_comparator(self, readback, setpoint):
        return setpoint-self.atol < readback < setpoint+self.atol


    def __init__(self, prefix, ch_name=None, atol=None, **kwargs):
        self._ch_name = ch_name
        self.atol = atol
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name 

class MonoThetaAxis(PVPositioner):

    setpoint = FCpt(EpicsSignal,'{self.prefix}Set{self._ch_name}', kind='normal')
    readback = FCpt(EpicsSignalRO,'{self.prefix}{self._ch_name}', kind = 'hinted')
    done     = FCpt(EpicsSignalRO,'{self.prefix}mirrorDone', kind='omitted')
    
    def __init__(self, prefix, ch_name=None, **kwargs):
        self._ch_name = ch_name
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name
    done_value = 1.0

class MonoAlphaBetaAxis(PVPositioner):

    setpoint = FCpt(EpicsSignal,'{self.prefix}Set{self._ch_name}', kind='normal')
    readback = FCpt(EpicsSignalRO,'{self.prefix}{self._ch_name}', kind = 'hinted')
    done     = FCpt(EpicsSignalRO,'{self.prefix}gratingDone', kind='omitted')
    
    def __init__(self, prefix, ch_name=None, **kwargs):
        self._ch_name = ch_name
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name
    done_value = 1.0

class Energy(PVPositioner):

    """
    Energy is a PVPositioner which also reimplements the get() method
    It is intended that this class is included as a component to monochromators
    
    """

    def __init__(self, prefix, *args, **kwargs):
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name 

    # this is an initial API 
    setpoint        = Cpt(EpicsSignal,      'monoSetEnergy' , kind='normal'  )
    readback        = Cpt(EpicsSignalRO,    'monoGetEnergy', labels={"pgm"},     kind='hinted') # the main output
    done            = Cpt(EpicsSignalRO,    'IStatus' , kind='omitted'             )
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
    grating_no      = Cpt(EpicsSignal, 'SetGratingNo', string='True',kind='config', labels={"pgm"}) #this takes some time, it needs either put completion or to be a positioner
    grating         = Cpt(EpicsSignalRO, 'lineDensity', kind='config') 

    eMin_eV         = Cpt(EpicsSignalRO, 'minEnergy', kind='config')
    eMax_eV         = Cpt(EpicsSignalRO, 'maxEnergy', kind='config')



class UndulatorMonoBase(SoftMonoBase):
    """
    UndulatorMonoBase contains all additional signals used for monochromators at undulator beamlines. 
    """

    ID_on           = Cpt(EpicsSignal, 'SetIdOn',kind='config', labels={"pgm"})
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


class ExitSlitEMIL(PVPositioner):
    """
    EMIL specific exit slit implementation. EMIL beamlines uses different PV name for setting the slit

    Since we always read ue48_pgm.en and not the entire mono device, making it hinted is acceptable for now. Should be a PVPositioner!
    """
    setpoint      = Cpt(EpicsSignal,  'SlitInput', kind='normal')
    readback =  Cpt(EpicsSignalRO, 'slitwidth', kind='hinted')
    done =Cpt(EpicsSignalRO, 'ES_STATUS', kind = 'omitted')
    done_value = 0
    branch = Cpt(EpicsSignal,  'SetBranch',  string='True',kind='config')


class ExitSlitMetrixs(ExitSlitBase):
    """
    Metrixs specific exit slit implementation. Metrixs beamlines uses different PV name for setting the slit
    """
    slitwidth       = Cpt(EpicsSignal,  'slitwidth', write_pv = 'SlitInput',     kind='config', labels={'pgm'})
    bandwidth       = Cpt(EpicsSignalRO,  'bandwidth'                       ,     kind='config')


class ExitSlitSlitUE52SGM(PVPositioner):
    """
    UE52SGM" specific exit slit implementation. 
    """

    def __init__(self, prefix, *args, **kwargs):
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name 

    # this is an initial API 
    setpoint        = Cpt(EpicsSignal,      'ES_0_Input' , kind='config'                                 )
    readback        = Cpt(EpicsSignalRO,    'ES_0_SW', labels={"sgm"},     kind='config') # the main output
    done            = Cpt(EpicsSignalRO,    'ES_0_STATUS' , kind='config'                                         )
    done_value      = 0
    
    # so that you can do for example ue48_pgm.en.get() rather than ue48_pgm.en.readback.get()
    def get(self):
        
        return self.readback.get()

class PGM(SoftMonoBase):
    """
    PGM is a core class for PGM monochromators
    """

    # PGMs has a full control over cff, so override it here
    cff             = Cpt(EpicsSignal, 'cff', write_pv='SetCff', kind='config')

    

class IdSlopeOffset(Device):
    """
    For undulator with ID Slope Offset control
    """
    energy1_nominal       = Cpt(EpicsSignal, 'Energy1', kind='omitted')
    energy1_measured      = Cpt(EpicsSignal, 'Meas1'  , kind='omitted')
    energy2_nominal       = Cpt(EpicsSignal, 'Energy2', kind='omitted')
    energy2_measured      = Cpt(EpicsSignal, 'Meas2'  , kind='omitted')

    IdSlope               = Cpt(EpicsSignal, 'aiIdSlope',write_pv = 'aoIdSlope', kind='config')
    IdSlope_old           = Cpt(EpicsSignal  , 'OldSlope' , kind='omitted')
    IdSlope_new           = Cpt(EpicsSignal  , 'NewSlope' , kind='omitted') 

    IdOffset              = Cpt(EpicsSignal, 'aiIdOffset',write_pv = 'aoIdOffset', kind='config')
    IdOffset_old          = Cpt(EpicsSignal  , 'OldOffset' , kind='omitted')
    IdOffset_new          = Cpt(EpicsSignal  , 'NewOffset' , kind='omitted')

    use_current           = Cpt(EpicsSignal  , 'UseCurSO.PROC' , kind='omitted')
    calculate             = Cpt(EpicsSignal  , 'CalcSlope.PROC'   , kind='omitted')
    accept                = Cpt(EpicsSignal  , 'AcceptSO.PROC' , kind='omitted')

    
   

class SGM(SoftMonoBase):
    """
    SGM is a core class for SGM monochromators
    """
    cff             = Cpt(EpicsSignalRO, 'c', kind='hinted')


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
class FlyingEnergy(BasicFlyer, Energy):

    def __init__(self, prefix='', *, limits=None, name=None, read_attrs=None,
                 configuration_attrs=None, parent=None, egu='', **kwargs):
        super().__init__(prefix=prefix, read_attrs=read_attrs,
                         configuration_attrs=configuration_attrs,
                         name=name, parent=parent, **kwargs)  
        self.complete_status = None
        self._acquiring = False
        self.t0 = 0
        self.readback.name = self.name
        
    #read_attrs = ['readback']
          
    #status is an mbbo record, I need to know what the different states are. 
    sweep_status    = Cpt(EpicsSignalRO, 'GetSweepState', kind='omitted')
    aktion          = Cpt(EpicsSignal, 'MonoAktion.PROC', kind='omitted') # writing different values to this pv causes different actions like init, start, stop
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
            
        if self.stop_signal is not None:
            self.stop_signal.put(self.stop_value, wait=False)
            
        #super().stop(success=success)

        
    def complete(self):
        """
        Wait for flying to be complete, get the status object that will tell us when we are done
        """
        def check_value(*,old_value, value, **kwargs):
            #Return True when the acquisition is complete, False otherwise.   
            if not self._acquiring:  #But only report done if acquisition was already started 
                return False
            return (value == 255 or value == 128)

        self.complete_status = SubscriptionStatus(self.sweep_status,check_value)

        return self.complete_status
       
class PGMEmil(IdSlopeOffset,UndulatorMonoBase,PGM):

    def __init__(self,prefix,  *args, **kwargs):
        self._finished_lock = threading.RLock() #create a lock 
        self._move_queue = []
        super().__init__(prefix,*args,**kwargs)
    
  
    positioning         = Cpt(EpicsSignal, 'multiaxis:mbbiMoveMode', write_pv='multiaxis:mbboSetMoveMode', string='True',kind='config')
    m2_translation      = Cpt(MonoTranslationAxis, '', ch_num='0',labels={"pgm"})
    grating_translation = Cpt(MonoTranslationAxis, '',atol = 0.5, ch_num='1',labels={"pgm"})
    grating_trans_sel   = Cpt(MonoTranslationAxisSelect,'',ch_num='1',labels={"pgm"})
    slit                = Cpt(ExitSlitEMIL, '')

    alpha               = Cpt(MonoAlphaBetaAxis, '',  ch_name='Alpha', settle_time=10.0)
    beta                = Cpt(MonoAlphaBetaAxis, '',  ch_name='Beta', settle_time=10.0)
    theta               = Cpt(MonoAlphaBetaAxis, '',  ch_name='Theta', settle_time=10.0)


    # experts settings of flyscan
    offset = Cpt(EpicsSignal,'GetSweepOffset', write_pv = 'SetSweepOffset' , kind='config')
    vmin_fak = Cpt(EpicsSignal,'GetSweepVminFak', write_pv = 'SetSweepVminFak' , kind='config')
    vmax_fak = Cpt(EpicsSignal,'GetSweepVmaxFak' , write_pv = 'SetSweepVmaxFak', kind='config')
    max_gain_output = Cpt(EpicsSignal, 'GetSweepOutLim', write_pv = 'SetSweepOutLim' , kind='config')
    open_loop_pvt =  Cpt(EpicsSignal,'GetSweepPVTM', write_pv ='SetSweepPVTM' , kind='config')
    hold_start = Cpt(EpicsSignal,'SetSweepSUSSTART1' , kind='config')
    hold_stop = Cpt(EpicsSignal,'SetSweepSUSSTOP1' , kind='config')
    hold_vel = Cpt(EpicsSignal,'SetSweepSUSVEL1' , kind='config')
    hold = Cpt(EpicsSignal,'SetSweepSUSM' , kind='config')
    filt_phi = Cpt(EpicsSignal,'SetSweepMFDly' , kind='config')
    filt_phi_ena = Cpt(EpicsSignal,'SetSweepMFOnOff' , kind='config')
    filt_psi = Cpt(EpicsSignal,'SetSweepGFDly' , kind='config')
    filt_psi_ena = Cpt(EpicsSignal,'SetSweepGFOnOff' , kind='config')
    cycle_time = Cpt(EpicsSignal,'SweepTics', write_pv = 'SetSweepTics' , kind='config')
    kp_mirror = Cpt(EpicsSignal,'SetKpMirror' , kind='config')
    kp_grating = Cpt(EpicsSignal,'SetKpGrating' , kind='config')
    gap_method = Cpt(EpicsSignal,'GetSweepGapMeth', write_pv = 'SetSweepGapMeth' , kind='config')

    
    def set_grating_400(self, wait=False):
                
        status = self.grating_trans_sel.move(1, wait=wait)
        self.grating_no.set(0)
        
        return(status)
    
    def set_grating_800(self,wait=False):
                
        status = self.grating_trans_sel.move(2, wait=wait)
        self.grating_no.set(1)
        
        return(status)
    
    def stop(self, success=False):

        del self._move_queue[:]

        exc_list = []

        for attr in self._sub_devices:
            dev = getattr(self, attr)

            if not dev.connected:
                continue

            try:
                dev.stop(success=success)
            except ExceptionBundle as ex:
                exc_list.extend(
                    [
                        ("{}.{}".format(attr, sub_attr), ex)
                        for sub_attr, ex in ex.exceptions.items()
                    ]
                )
            except Exception as ex:
                exc_list.append((attr, ex))
                self.log.exception("Device %s (%s) stop failed", attr, dev)

        if exc_list:
            exc_info = "\n".join(
                "{} raised {!r}".format(attr, ex) for attr, ex in exc_list
            )
            raise ExceptionBundle(
                "{} exception(s) were raised during stop: \n"
                "{}".format(len(exc_list), exc_info),
                exceptions=dict(exc_list),
            )
        
    

    def restore(self, d: Dict[str, Any]):

        """
        parameter_dict : ordered_dict

        A dictionary containing names of signals (from a baseline reading)
        """

        #first pass determine which parameters are configuration parameter
        self.ID_on.set(0)

        for config_attr in self.configuration_attrs:

            #Make the key as it would be found in d

            param_name = self.name + "_" + config_attr.replace('.','_')
            
            if param_name in d and param_name != self.ID_on.name:
                if hasattr(self,config_attr+'.write_access'):
                    if getattr(self,config_attr+'.write_access'):
                        getattr(self, config_attr).set(d[param_name]).wait()

        #second pass. We know we are a positioner, so let's restore the position
                        
        st = DeviceStatus(device=self)
        #populate the move queue 
        positioners = [self.grating_translation,self.slit,self.en] #grating, then slit then energy
        positions = []

        for positioner in positioners:

            param_name = positioner.setpoint.name
            if param_name in d:
                positions.append(d[param_name])
            
        self._move_queue[:] = list(zip(positioners, positions))
        pending_status = []
    
        #Define a recursive function that itterates through the queue 
        def move_next(status=None, obj=None):
            
            with self._finished_lock:

                if pending_status:
                    last_status = pending_status[-1]
                    if not last_status.success:
                        self.log.error("Failing due to last motion")
                        st.set_exception(last_status.exception)
                        return

                try:
                    real, position = self._move_queue.pop(0)
                except IndexError:
                    #we've finished the queue
                    

                    self.ID_on.set(d[self.ID_on.name]).wait()

                    st.set_finished()
                    return 

                status = real.move(
                        position,
                        wait=False,
                        moved_cb=move_next
                    )
                pending_status.append(status)
        
        #start the queue
        move_next()
          
        return st
   

    
# the name of these two classe has to be changed to be EMIL specific
class PGMSoft(PGMEmil):
    en = Cpt(FlyingEnergy,'')
    grating_800_temp    = FCpt(EpicsSignalRO,  'MONOY02U112L:Grating1T1', kind='normal', labels={'pgm'})
    grating_400_temp    = FCpt(EpicsSignalRO,  'MONOY02U112L:Grating2T1', kind='normal', labels={'pgm'})
    mirror_temp         = FCpt(EpicsSignalRO,  'MONOY02U112L:MirrorT1',   kind='normal', labels={'pgm'})



    #read_attrs          = ['en.readback']



class PGMHard(PGMEmil):
    en = Cpt(FlyingEnergy,'')
    grating_800_temp    = FCpt(EpicsSignalRO,  'MONOY01U112L:Grating1T1', kind='normal', labels={'pgm'})
    grating_400_temp    = FCpt(EpicsSignalRO,  'MONOY01U112L:Grating2T1', kind='normal', labels={'pgm'})
    mirror_temp         = FCpt(EpicsSignalRO,  'MONOY01U112L:MirrorT1',   kind='normal', labels={'pgm'})
    #read_attrs          = ['en.readback']
    
    
    
class PGM_Aquarius(UndulatorMonoBase, PGM):

    # We want to inherit everything from UnUndulatorMonoBase but rewrite these attributes to add settle time and a new attribute fix_theta
    # the read PV at Aquarius is different compared to UndulatorMonoBase
    #harmonic        = Cpt(EpicsSignal, 'ShowIdHarmonic', write_pv = 'Harmonic', string='True',kind='config') ? 
    
    alpha            = Cpt(MonoAlphaBetaAxis, '',  ch_name='Alpha', settle_time=10.0, kind='config')
    beta             = Cpt(MonoAlphaBetaAxis, '',  ch_name='Beta',  settle_time=10.0, kind='config', labels={'pgm'})
    theta            = Cpt(MonoThetaAxis, '',  ch_name='Theta', settle_time=10.0, kind='config', labels={'pgm'})
    fix_theta        = Cpt(EpicsSignal,  'FixThetaAngle', write_pv = 'SetFixThetaAng', kind='config')
    read_attrs       = ['en.readback', 'beta.readback', 'theta.readback']


# labels need to be changed from pgm to sgm. How can this be done when importing from Energy and UndulatorMonoBase class?  


class SGMMetrixs(UndulatorMonoBase, ExitSlitMetrixs, SGM):    

    harmonic         = Cpt(EpicsSignal, 'ShowIdHarmonic', write_pv = 'Harmonic', string='True',kind='config')
    #cff             = Cpt(EpicsSignalRO, 'c', kind='hinted')
    
    mirror_angle     = Cpt(PGMScannableAxis, '',  ch_name='Phi', settle_time=10.0, kind='config')
    grating_angle    = Cpt(PGMScannableAxis, '',  ch_name='Psi', settle_time=10.0, kind='config')
    alpha            = Cpt(MonoAlphaBetaAxis, '',  ch_name='Alpha', settle_time=2.0, kind='config')
    beta             = Cpt(MonoAlphaBetaAxis, '',  ch_name='Beta',  settle_time=0.1, kind='config', labels={'sgm'})
    theta            = Cpt(MonoThetaAxis, '',  ch_name='Theta', settle_time=0.1, kind='config', labels={'sgm'})
    
    grating_radius   = Cpt(EpicsSignal, 'RG', write_pv = 'SetRG', string='True',kind='config')
    entrancearm      = Cpt(EpicsSignal, 'entrancearm', write_pv = 'SetEntrance', string='True',kind='config')
    zero_order_angle = Cpt(EpicsSignalRO, 'MZeroOrder', string='True',kind='config')
    position_timer   = Cpt(EpicsSignal, 'PositionTimer', write_pv = 'SetPositionTimer', string='True',kind='config')
    


class SGMUE52(IdSlopeOffset, UndulatorMonoBase, PGM):    
    en = Cpt(FlyingEnergy,'')
    slitwidth        = Cpt(ExitSlitSlitUE52SGM,'')
    harmonic         = Cpt(EpicsSignal, 'ShowIdHarmonic', write_pv = 'Harmonic', string='True',kind='config')
    #cff             = Cpt(EpicsSignalRO, 'c', kind='hinted')
    
    mirror_angle     = Cpt(PGMScannableAxis, '',  ch_name='Phi', settle_time=1.0, kind='config')
    grating_angle    = Cpt(PGMScannableAxis, '',  ch_name='Psi', settle_time=1.0, kind='config')

    #alpha            = Cpt(MonoComparatorAxis, '',  ch_name='Alpha', settle_time=2.0, kind='config')
    #beta             = Cpt(MonoComparatorAxis, '',  ch_name='Beta',  settle_time=0.1, kind='config', labels={'sgm'})
    #theta            = Cpt(MonoComparatorAxis, '',  ch_name='Theta', settle_time=0.1, kind='config', labels={'sgm'})
    
    #
    #alpha            = Cpt(MonoAlphaBetaAxis, '',  ch_name='Alpha', settle_time=2.0, kind='config')
    #beta             = Cpt(MonoAlphaBetaAxis, '',  ch_name='Beta',  settle_time=0.1, kind='config', labels={'sgm'})
    #theta            = Cpt(MonoThetaAxis, '',  ch_name='Theta', settle_time=0.1, kind='config', labels={'sgm'})
        
    # neverage ?
    # TouchDiff ?
    # StopDiff ?
    # Diff ?     
    # IdSlope ?
    # IdOffset ? 
    #position_timer   = Cpt(EpicsSignal, 'PositionTimer', write_pv = 'SetPositionTimer', string='True',kind='config')
    

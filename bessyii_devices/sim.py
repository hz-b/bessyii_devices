##set up some test devices
from ophyd.sim import SynAxis
from bessyii_devices.positioners import PVPositionerDone
from bessyii_devices.device import BESSYDevice as Device
import time as ttime
import numpy as np

class SimPositionerDone(SynAxis, PVPositionerDone):

    """
    A PVPositioner which reports done immediately AND conforms to the standard of other positioners with signals for 
    
    setpoint
    readback
    done
    
    
    """
    def _setup_move(self, position):
        '''Move and do not wait until motion is complete (asynchronous)'''
        self.log.debug('%s.setpoint = %s', self.name, position)
        self.setpoint.put(position)
        if self.actuate is not None:
            self.log.debug('%s.actuate = %s', self.name, self.actuate_value)
            self.actuate.put(self.actuate_value)
        self._toggle_done()
        
    def __init__(self,
                 name,
                 readback_func=None,
                 value=0,
                 delay=0,
                 precision=3,
                 parent=None,
                 labels=None,
                 kind=None,**kwargs):
        super().__init__(name=name,prefix='', parent=parent, labels=labels, kind=kind,readback_func=readback_func,delay=delay,precision=precision,
                         **kwargs)
        self.set(value)

from ophyd.status import DeviceStatus, MoveStatus
from ophyd import ttime
from ophyd.utils import (
    InvalidState,
    StatusTimeoutError,
    UnknownStatusFailure,
    WaitTimeoutError,
)
import threading

class DodgyMotor(SimPositionerDone):
    
    def __init__(self,
                 name,
                 readback_func=None,
                 value=0,
                 delay=0,
                 precision=3,
                 parent=None,
                 labels=None,
                 kind=None,**kwargs):
        super().__init__(name=name, parent=parent, labels=labels, kind=kind,readback_func=readback_func,delay=delay,precision=precision,
                         **kwargs)
        self.set(value)
        self.timeout = self.delay - 1
    
    def set(self, value):
        old_setpoint = self.sim_state['setpoint']
        self.sim_state['setpoint'] = value
        self.sim_state['setpoint_ts'] = ttime.time()
        self.setpoint._run_subs(sub_type=self.setpoint.SUB_VALUE,
                                old_value=old_setpoint,
                                value=self.sim_state['setpoint'],
                                timestamp=self.sim_state['setpoint_ts'])

        def update_state():
            old_readback = self.sim_state['readback']
            self.sim_state['readback'] = self._readback_func(value)
            self.sim_state['readback_ts'] = ttime.time()
            self.readback._run_subs(sub_type=self.readback.SUB_VALUE,
                                    old_value=old_readback,
                                    value=self.sim_state['readback'],
                                    timestamp=self.sim_state['readback_ts'])
            self._run_subs(sub_type=self.SUB_READBACK,
                           old_value=old_readback,
                           value=self.sim_state['readback'],
                           timestamp=self.sim_state['readback_ts'])

        st = DeviceStatus(device=self)
        if self.delay:
            def sleep_and_finish():
                ttime.sleep(self.delay)
                update_state()
                
            threading.Thread(target=sleep_and_finish, daemon=True).start()
            
        else:
            update_state()
            
        
        st.set_exception(TimeoutError)
        return st


m1 = SimPositionerDone(name='m1' )
m2 = SimPositionerDone(name='m2')
m3 = SimPositionerDone(name='m3')


from ophyd import EpicsMotor, Signal, Component as Cpt


class SimStage(Device):
    
    x = Cpt(SimPositionerDone)
    y = Cpt(SimPositionerDone)
    config_param = Cpt(Signal, kind='config')
    
class SimStageOfStage(Device):
    
    a = Cpt(SimStage)
    b= Cpt(SimStage)
    config_param = Cpt(Signal, kind='config')

stage = SimStageOfStage(name = 'stage')



#Create a PseudoPositioner

from ophyd.pseudopos import (
    PseudoSingle,
    pseudo_position_argument,
    real_position_argument
)
from bessyii_devices.positioners import PseudoPositionerBessy as PseudoPositioner
from ophyd import Component


class Pseudo3x3(PseudoPositioner):
    """
    Interface to three positioners in a coordinate system that flips the sign.
    """
    pseudo1 = Component(PseudoSingle, limits=(-10, 10), egu='a')
    pseudo2 = Component(PseudoSingle, limits=(-10, 10), egu='b')
    pseudo3 = Component(PseudoSingle, limits=(-10, 10), egu='c')
    
    #add some offset to distinguish readback and setpoint
    real1 = Component(SimPositionerDone,value=0.1,readback_func=lambda x: 2*x)
    real2 = Component(SimPositionerDone,value=0.1,readback_func=lambda x: 2*x)
    real3 = Component(SimPositionerDone,value=0.1,readback_func=lambda x: 2*x)

    @pseudo_position_argument
    def forward(self, pseudo_pos):
        "Given a position in the psuedo coordinate system, transform to the real coordinate system."
        return self.RealPosition(
            real1=-pseudo_pos.pseudo1,
            real2=-pseudo_pos.pseudo2,
            real3=-pseudo_pos.pseudo3
        )

    @real_position_argument
    def inverse(self, real_pos):
        "Given a position in the real coordinate system, transform to the pseudo coordinate system."
        return self.PseudoPosition(
            pseudo1=-real_pos.real1,
            pseudo2=-real_pos.real2,
            pseudo3=-real_pos.real3
        )

p3 = Pseudo3x3(name='p3')


#integer detector

# let's make a simulated detector.


from ophyd.sim import SynGauss, SynAxis
from ophyd import Component as Cpt
from ophyd import Signal
import numpy as np

class SynGaussMonitorInteger(SynGauss):
    
    """
    An extension of the SynGauss device to include additional parameters that help us clasify it for generating NeXus files
    
    
    """
    mode = Cpt(Signal, kind='config')
    preset = Cpt(Signal, value = 0.1, kind='config')
    
    def __init__(self, prefix,mode, *args, **kwargs):
        
        super().__init__(prefix,*args,**kwargs)
        self.mode.put(mode)
        
    def _compute(self):
        m = self._motor.read()[self._motor_field]['value']
        # we need to do this one at a time because
        #   - self.read() may be screwed with by the user
        #   - self.get() would cause infinite recursion
        Imax = self.Imax.get()
        center = self.center.get()
        sigma = self.sigma.get()
        noise = self.noise.get()
        noise_multiplier = self.noise_multiplier.get()
        v = Imax * np.exp(-(m - center) ** 2 /
                          (2 * sigma ** 2))
        if noise == 'poisson':
            v = int(self.random_state.poisson(np.round(v), 1))
        elif noise == 'uniform':
            v += self.random_state.uniform(-1, 1) * noise_multiplier
        return int(v)
        
        
sim_motor = SimPositionerDone(name='sim_motor' )
noisy_det_monitor = SynGaussMonitorInteger('noisy_det_monitor','timer',sim_motor, 'sim_motor', center=0, Imax=1000, sigma=10,noise='uniform',noise_multiplier=4)

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

class SimMono(SimStageOfStage):

    en = Cpt(SimPositionerDone)
    grating = Cpt(SimPositionerDone)

    def restore(self, d: Dict[str, Any]):

        """
        parameter_dict : ordered_dict

        A dictionary containing names of signals (from a baseline reading)
        """

        #first pass determine which parameters are configuration parameters
        
        seen_attrs = []

        for config_attr in self.configuration_attrs:

            #Make the key as it would be found in d

            param_name = self.name + "_" + config_attr.replace('.','_')
            
            if param_name in d:
                if hasattr(self,config_attr+'.write_access'):
                    if getattr(self,config_attr+'.write_access'):
                        getattr(self, config_attr).set(d[param_name]).wait()

        #second pass. We know we are a positioner, so let's restore the position
                
        #In this test device we will always restore a.x then a.y, then b.y then b.x
        self.a.x.move(d[self.a.x.name +  "_setpoint"]).wait() # we will wait for it to complete
        self.a.y.move(d[self.a.y.name +  "_setpoint"]).wait()
        self.b.y.move(d[self.b.y.name +  "_setpoint"]).wait() # we will wait for it to complete
        sta = self.b.x.move(d[self.b.x.name +  "_setpoint"])
        return sta

sim_mono = SimMono(name = 'sim_mono')



## Sim Hexapod

class SimHexapod(PseudoPositioner):
    """
    
    A  simulated class for all hexapods controlled by geo-brick motion controllers
    Using a PseudoPositioner allows us to read and set positions as groups like this:
    
      hex.move(tx,ty,tz,rx,ry,rz)
    
    as well as individually like:
    
      hex.ty.move(3700)
    
    The _concurrent_move method is rewritten to allow all axes to be written first before the move is executed.
    
    The error bits from the axes are reset before each move by sending the command '&1a' to the geobrick
    
    Note, if you are doing a mesh scan with an instance of this class, you should use 'snake' so that only one axes is moved at once
    
    
    """
    #Pseudo Axes
    rx = Cpt(PseudoSingle)
    ry = Cpt(PseudoSingle)
    rz = Cpt(PseudoSingle)
    tx = Cpt(PseudoSingle)
    ty = Cpt(PseudoSingle)
    tz = Cpt(PseudoSingle)

    #Real Axes
    rrx = Cpt(SimPositionerDone,kind='normal')
    rry = Cpt(SimPositionerDone,kind='normal')
    rrz = Cpt(SimPositionerDone,kind='normal')
    rtx = Cpt(SimPositionerDone,kind='normal')
    rty = Cpt(SimPositionerDone,kind='normal')
    rtz = Cpt(SimPositionerDone,kind='normal')
    
    start_immediately = Cpt(Signal, kind = 'omitted')
    do_it = Cpt(Signal, kind = 'omitted')
    multiaxis_running = Cpt(Signal , kind='omitted'         )
    pmac = Cpt(Signal, kind = 'omitted') #send &1a to clear errors before any move

    @pseudo_position_argument
    def forward(self, pseudo_pos):
        '''Run a forward (pseudo -> real) calculation'''
        return self.RealPosition(rrx=pseudo_pos.rx,
                                 rry=pseudo_pos.ry,
                                 rrz=pseudo_pos.rz,
                                 rtx=pseudo_pos.tx,
                                 rty=pseudo_pos.ty,
                                 rtz=pseudo_pos.tz
                                 )


    @real_position_argument
    def inverse(self, real_pos):
        '''Run an inverse (real -> pseudo) calculation'''
        return self.PseudoPosition(rx=real_pos.rrx,
                                 ry=real_pos.rry,
                                 rz=real_pos.rrz,
                                 tx=real_pos.rtx,
                                 ty=real_pos.rty,
                                 tz=real_pos.rtz
                                 )

    def _concurrent_move(self, real_pos, **kwargs):
        '''Move all real positioners to a certain position, in parallel'''
        
        #self.pmac.put('&1a')
        #self.start_immediately.put(0)
        for real, value in zip(self._real, real_pos):
            self.log.debug('[concurrent] Moving %s to %s', real.name, value)
            real.setpoint.put(value)
        
        #self.start_immediately.put(1)
        self.do_it.put(1)
        self.do_it.put(0)

        #Now having put the values to the axes we need to set a done signal to 0, then initiate the move and add a callback which will
        # move the done write 

    def _real_finished(self, *args,**kwargs):
        '''Callback: A single real positioner has finished moving. 	Used for asynchronous motion, if all have finished moving 	then fire a callback (via Positioner._done_moving)'''
        with self._finished_lock:
                
            self._done_moving() #Since we are in simulation

    def __init__(self,  *args, **kwargs):
        
        super().__init__(*args,**kwargs)

        self.do_it.subscribe(self._real_finished) # for simulated move

sim_hex = SimHexapod(name="sim_hex")

class SimSMUHexapod(SimHexapod):

    """
    A hexapod that can change between two different co-ordinate systems
    """
    _real = ['rrx','rry','rrz','rtx','rty','rtz']
    choice = Cpt(SimPositionerDone,kind="normal")

sim_smu = SimSMUHexapod(name="sim_smu")
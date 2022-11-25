##set up some test devices
from ophyd.sim import SynAxis
from bessyii_devices.positioners import PVPositionerDone
from bessyii_devices.device import BESSYDevice as Device
from ophyd import Signal,Component as Cpt
from ophyd.sim import SynGauss, SynAxis
import threading
from ophyd.status import DeviceStatus
import time
from ophyd.pseudopos import (
    PseudoSingle,
    pseudo_position_argument,
    real_position_argument
)
from bessyii_devices.positioners import PseudoPositionerBessy as PseudoPositioner
from ophyd import ttime
from ophyd.utils import (
    InvalidState,
    StatusTimeoutError,
    UnknownStatusFailure,
    WaitTimeoutError,
)
import threading
import time as ttime
import numpy as np
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


from ophyd import SoftPositioner


class ConfigDev(Device):

    config_param_a = Cpt(Signal, kind='config')
    config_param_b = Cpt(Signal, kind='config')
    config_param_c = Cpt(Signal, kind='config')

class SimPositionerDone(SynAxis,SoftPositioner):

    config_dev_1 = Cpt(ConfigDev, kind='config')
    config_dev_2 = Cpt(ConfigDev, kind='config')

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
        sta =  self.move(d[self.name + "_setpoint"])   
        return sta
    
    def __init__(self,name, **kwargs):
        super().__init__(name=name, **kwargs)
        self.readback.name = self.name 
        self.setpoint.set(0)





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




class SimStage(Device):
    
    x = Cpt(SimPositionerDone)
    y = Cpt(SimPositionerDone)
    config_param = Cpt(Signal, kind='config')
    
class SimStageOfStage(Device):
    
    a = Cpt(SimStage)
    b= Cpt(SimStage)
    config_param = Cpt(Signal, kind='config')

class Pseudo3x3(PseudoPositioner):
    """
    Interface to three positioners in a coordinate system that flips the sign.
    """
    pseudo1 = Cpt(PseudoSingle, limits=(-10, 10), egu='a')
    pseudo2 = Cpt(PseudoSingle, limits=(-10, 10), egu='b')
    pseudo3 = Cpt(PseudoSingle, limits=(-10, 10), egu='c')
    
    #add some offset to distinguish readback and setpoint
    real1 = Cpt(SimPositionerDone,value=0.1,readback_func=lambda x: 2*x, egu="egu", limits=(-10, 10))
    real2 = Cpt(SimPositionerDone,value=0.1,readback_func=lambda x: 2*x, egu="egu", limits=(-10, 10))
    real3 = Cpt(SimPositionerDone,value=0.1,readback_func=lambda x: 2*x, egu="egu", limits=(-10, 10))

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



#integer detector

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
        
   


class SimMono(SimStageOfStage):

    def __init__(self,  *args, **kwargs):
        self._finished_lock = threading.RLock() #create a lock 
        
        super().__init__(*args,**kwargs)


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
                        
        positioners = [self.a.x,self.a.y,self.b.y,self.b.x] #in the order we want to restore

        st = DeviceStatus(device=self)
        
        def set_positions():
                self.a.x.move(d[self.a.x.name + "_setpoint"]).wait()
                self.a.y.move(d[self.a.y.name + "_setpoint"]).wait()
                self.b.y.move(d[self.b.y.name + "_setpoint"]).wait()
                self.b.x.move(d[self.b.x.name + "_setpoint"]).wait()

                st.set_finished()

        threading.Thread(target=set_positions, daemon=True).start()

        return st
            




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
    rrx = Cpt(SimPositionerDone,kind='normal', egu="egu", limits=(-10, 10))
    rry = Cpt(SimPositionerDone,kind='normal', egu="egu", limits=(-10, 10))
    rrz = Cpt(SimPositionerDone,kind='normal', egu="egu", limits=(-10, 10))
    rtx = Cpt(SimPositionerDone,kind='normal', egu="egu", limits=(-10, 10))
    rty = Cpt(SimPositionerDone,kind='normal', egu="egu", limits=(-10, 10))
    rtz = Cpt(SimPositionerDone,kind='normal', egu="egu", limits=(-10, 10))
    
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




class SimSMUHexapod(SimHexapod):

    """
    A hexapod that can change between two different co-ordinate systems
    """
    _real = ['rrx','rry','rrz','rtx','rty','rtz']
    choice = Cpt(SimPositionerDone,kind="normal", egu="egu", limits=(-10, 10))

    


#Define some devices:

m1 = SimPositionerDone(name='m1' , egu="egu", limits=(-10, 10))
m2 = SimPositionerDone(name='m2', egu="egu", limits=(-10, 10))
m3 = SimPositionerDone(name='m3', egu="egu", limits=(-10, 10))
sim_motor = SimPositionerDone(name='sim_motor' , egu="egu", limits=(-10, 10))
noisy_det_monitor = SynGaussMonitorInteger('noisy_det_monitor','timer',sim_motor, 'sim_motor', center=0, Imax=1000, sigma=10,noise='uniform',noise_multiplier=4)
stage = SimStageOfStage(name = 'stage')
p3 = Pseudo3x3(name='p3')
sim_mono = SimMono(name = 'sim_mono')
sim_hex = SimHexapod(name="sim_hex")
sim_smu = SimSMUHexapod(name="sim_smu")
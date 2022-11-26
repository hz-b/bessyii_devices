from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device, DerivedSignal,PseudoPositioner,PseudoSingle
from ophyd import Component as Cpt
from ophyd.pseudopos import (pseudo_position_argument,
                             real_position_argument)
from ophyd.signal import Signal, SignalRO
from ophyd import FormattedComponent as FCpt
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

class PVPositionerBessy(PVPositioner):

    def restore(self, d: Dict[str, Any]):

        """
        parameter_dict : ordered_dict

        A dictionary containing names of signals (from a baseline reading)
        """

        #first pass determine which parameters are configuration parameters
        
        sta = []

        for config_attr in self.configuration_attrs:

            #Make the key as it would be found in d

            param_name = self.name + "_" + config_attr.replace('.','_')
            
            if param_name in d:
                if hasattr(self,config_attr+'.write_access'):
                    if getattr(self,config_attr+'.write_access'):
                        getattr(self, config_attr).set(d[param_name]).wait()

        #second pass. We know we are a positioner, so let's restore the position
        if self.name + "_setpoint" in d:
            sta =  self.move(d[self.name + "_setpoint"],wait=False)   
        return sta
    
    def __init__(self, prefix, **kwargs):
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name 

class PseudoPositionerBessy(PseudoPositioner):

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

        #second pass. We know we are a pseudo positioner, so let's restore the position
                

        # create a position dictionary
        position_dict = {}
        
        #calculate the values that the real positioners were set to
        for real_axis in self.real_positioners:
            
            signal_name = real_axis.setpoint.name
            signal_value = d[signal_name.replace('.','_')]
            position_dict[real_axis._attr_name] = signal_value
        
        #From that real position derive the pseudo position we need to drive to
        pseudo_pos = self.inverse(position_dict)
        
        #Use that position dictionary as the setpoint

        sta =  self.move(pseudo_pos)   
        return sta


#https://github.com/pcdshub/pcdsdevices/blob/master/pcdsdevices/signal.py
class InternalSignal(SignalRO):
    """
    Class Signal that stores info but should only be updated by the class.
    SignalRO can be updated with _readback, but this does not process
    callbacks. For the signal to behave normally, we need to bypass the put
    override.
    To put to one of these signals, simply call put with force=True
    """

    def put(self, value, *, timestamp=None, force=False):
        return Signal.put(self, value, timestamp=timestamp, force=force)

    def set(self, value, *, timestamp=None, force=False):
        return Signal.set(self, value, timestamp=timestamp, force=force)

# based on https://github.com/pcdshub/pcdsdevices/blob/master/pcdsdevices/pv_positioner.py with readback included
class PVPositionerDone(PVPositionerBessy):
    """
    PV Positioner with no readback that reports done immediately.
    Optionally, this PV positioner can be configured to skip small moves,
    e.g. moves that are smaller than the atol value.
    Parameters
    ----------
    prefix: str
        PV prefix for the request setpoint. This should always be a hutch name.
    name: str, required keyword
        Name to use for this device in log messages, data streams, etc.
    skip_small_moves: bool, optional
        Defaults to False. If True, ignores move requests that are smaller
        than the atol factor.
        This can be very useful for synchronized energy scans where the ACR
        side of the process can be very slow, but does not necessarily need to
        happen at every step. Rather than design complicated scan patterns, we
        can skip the small moves here and move the monochromater and beam
        request devices in parallel.
    
    """

    # Override setpoint, readback in subclass
    setpoint = None
    readback = None

    done = Cpt(InternalSignal, value=0,kind = 'omitted')
    done_value = 1

    
    def _setup_move(self, position):
       
        super()._setup_move(position)
        self._toggle_done()

    def _toggle_done(self):
        self.done.put(0, force=True)
        self.done.put(1, force=True)
        
        

class PVPositionerComparator(PVPositionerBessy):
    """
    PV Positioner with a software done signal.
    The done state is set by a comparison function defined in the class body.
    The comparison function takes two arguments, readback and setpoint,
    returning True if we are close enough to be considered done or False if we
    are too far away.
    """

    # Override setpoint, readback in subclass
    setpoint = None
    readback = None

    done = Cpt(InternalSignal, value=0,kind = 'omitted' )
    done_value = 1

    # Optionally override limits to a 2-element tuple in subclass
    limits = None

    def __init__(self, prefix, *, name, **kwargs):
        self._last_readback = None
        self._last_setpoint = None
        super().__init__(prefix, name=name, **kwargs)
        if None in (self.setpoint, self.readback):
            raise NotImplementedError('PVPositionerComparator requires both '
                                      'a setpoint and a readback signal to '
                                      'compare!')

    def done_comparator(self, readback, setpoint):
        """Override done_comparator in subclass."""
        raise NotImplementedError('Must implement a done comparator!')

    def __init_subclass__(cls, **kwargs):
        """Set up callbacks in subclass."""
        super().__init_subclass__(**kwargs)
        if None not in (cls.setpoint, cls.readback):
            cls.setpoint.sub_value(cls._update_setpoint)
            cls.readback.sub_value(cls._update_readback)

    def _update_setpoint(self, *args, value, **kwargs):
        """Callback to cache the setpoint and update done state."""
        self._last_setpoint = value
        # Always set done to False when a move is requested
        # This means we always get a rising edge when finished moving
        # Even if the move distance is under our done moving tolerance
        self.done.put(0, force=True)
        self._update_done()

    def _update_readback(self, *args, value, **kwargs):
        """Callback to cache the readback and update done state."""
        self._last_readback = value
        self._update_done()

    def _update_done(self):
        """Update our status to done if we pass the comparator."""
        if None not in (self._last_readback, self._last_setpoint):
            is_done = self.done_comparator(self._last_readback,
                                           self._last_setpoint)
            self.done.put(int(is_done), force=True)
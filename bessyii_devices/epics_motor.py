from ophyd.epics_motor import EpicsMotor
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
from ophyd.status import DeviceStatus, StatusBase, SubscriptionStatus, wait as status_wait


class EpicsMotorBessy(EpicsMotor):

    def restore(self, d: Dict[str, Any]):

        """
        parameter_dict : ordered_dict

        A dictionary containing names of signals (from a baseline reading)
        """

        #first pass determine which parameters are configuration parameters
        
        sta = None

        for config_attr in self.configuration_attrs:

            #Make the key as it would be found in d

            param_name = self.name + "_" + config_attr.replace('.','_')
            
            if param_name in d:
                if hasattr(self,config_attr+'.write_access'):
                    if getattr(self,config_attr+'.write_access'):
                        getattr(self, config_attr).set(d[param_name]).wait()

        #second pass. We know we are a positioner, so let's restore the position
        if self._restore_readback == True:
            if self.name+ "_user_readback" in d:
                sta =  self.move(d[self.name+"_user_readback"],wait=False) 
            else:
                sta = None  
        else:
            if self.name + "_user_setpoint" in d:
                sta =  self.move(d[self.name + "_user_setpoint"],wait=False)   
            else:
                sta = None
        
       
        return sta
    
    def __init__(self, prefix,restore_readback=False, **kwargs):
        super().__init__(prefix, **kwargs)
        self._restore_readback = restore_readback

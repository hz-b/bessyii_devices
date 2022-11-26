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

class EpicsMotorBessy(EpicsMotor):

    def restore(self, d: Dict[str, Any]):

        """
        parameter_dict : ordered_dict

        A dictionary containing names of signals (from a baseline reading)
        """

        #first pass determine which parameters are configuration parameters
        
        sta =None

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
    
    #def __init__(self, prefix, **kwargs):
    #    super().__init__(prefix, **kwargs)
    #    self.readback.name = self.name 
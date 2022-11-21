from ophyd import Device
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

class BESSYDevice(Device):

    """
    Based on the Device class, this adds an extra method called restore which can restore the configuration and position of positioners

    It is passed an ordered dict of parameter names and values. the method first works out which ones are configuration parameters, 
    restores them, then restores any positioner values. 

    It is intended that this method is overwritten for devices which need some special restore order (like a hexapod or monochromator)
    """

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
                getattr(self, config_attr).set(d[param_name]).wait()
                seen_attrs.append(param_name)

                
from ophyd import Device
from ophyd.status import AndStatus
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

    def restore(self, d: Dict[str, Any]) -> list: 

        """
        parameter_dict : ordered_dict

        A dictionary containing names of signals (from a baseline reading)

        returns a list of status objects for things that will take time
        """

        #first pass determine which parameters are configuration parameters

        
        status_objects = []
        for config_attr in self.configuration_attrs:

            #Make the key as it would be found in d

            param_name = self.name + "_" + config_attr.replace('.','_')
            
            if param_name in d:
                if hasattr(self,config_attr+'.write_access'):
                    if getattr(self,config_attr+'.write_access'):
                        ret = getattr(self, config_attr).set(d[param_name]).wait()
                        status_objects.append(ret)
                        

        #now call restore on any component devices
        for component_name in self.component_names:
            component = getattr(self,component_name)
            
            if hasattr(component, "restore"):
                component_status_list = component.restore(d) #should return a status object or None
                if component_status_list:
                    status_objects = status_objects + component_status_list
               
                """
                
                if ret and comp_ret:
                    ret = AndStatus(ret,comp_ret)
                elif comp_ret:
                    ret = comp_ret
                """

        return status_objects
                            


                
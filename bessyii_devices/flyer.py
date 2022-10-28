
from ophyd.utils import OrderedDefaultDict
from ophyd.status import SubscriptionStatus, DeviceStatus
from ophyd import Device, EpicsSignal, EpicsSignalRO
import numpy as np
import os
import random
import threading
import time as ttime
import uuid
import weakref
import warnings
from ophyd.status import wait

from collections import deque, OrderedDict
from tempfile import mkdtemp

from ophyd.signal import Signal, EpicsSignal, EpicsSignalRO
from ophyd.areadetector.base import EpicsSignalWithRBV
from ophyd.status import DeviceStatus, StatusBase
from ophyd.device import (Device, Component as Cpt,
                     DynamicDeviceComponent as DDCpt, Kind)
from types import SimpleNamespace
from ophyd.pseudopos import (PseudoPositioner, PseudoSingle,
                        real_position_argument, pseudo_position_argument)
from ophyd.positioner import SoftPositioner
from ophyd.utils import ReadOnlyError, LimitError
from ophyd import PVPositioner
from ophyd import Component as Cpt
from .positioners import PVPositionerComparator
import time


from ophyd import Device, Component as Cpt, EpicsSignal, EpicsSignalRO
from ophyd.status import DeviceStatus, StatusBase

from ophyd.utils import OrderedDefaultDict
from ophyd.status import SubscriptionStatus, DeviceStatus
import os
import errno
from galvani import BioLogic as BL
import pandas as pd
import glob
from pathlib import Path
import os
from pprint import pprint
import threading
from time import sleep

class BiologicPotentiostat(Device):
    
    """
    data_dir: path
    
        The path to the location containing the files
    
    sim_delay: int (optional)
        
        the delay in seconds before the complete status will return true
    
    example: 
    
        data_dir = "/home/jupyter-will/EMIL_Bluesky_Notebooks/Biologic/Data/"
        biologic = BiologicPotentiostat("SISSY2EX:BIOLOGIC:", name="biologic",sim_delay=10, data_dir=data_dir)
    """
    
    trigger_out = Cpt(EpicsSignal, "TRIGGER:SEND", kind='omitted', put_complete=True)
    done = Cpt(EpicsSignalRO, "TRIGGER:DONE", kind='omitted')
    
    def __init__(self, prefix='',data_dir=None, *, limits=None, name=None, read_attrs=None,
                 configuration_attrs=None, parent=None,sim_delay=None, egu='', **kwargs):
        super().__init__(prefix=prefix, read_attrs=read_attrs,
                         configuration_attrs=configuration_attrs,
                         name=name, parent=parent, **kwargs)  
        self.kickoff_status = None
        self.complete_status = None
        self._acquiring = False
        self.t0 = 0
        self.sim = sim_delay
        if data_dir != None:
            if os.path.exists(data_dir):
                self.data_dir = data_dir
            else:
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), data_dir)
        
        
    def kickoff(self):
        """
        Trigger the acquisition to start, take a note of the start time
        """
        

        self.complete_status = DeviceStatus(self)
        self._acquiring = True
        
        #send the trigger
        status = self.trigger_out.set(1)
        self.t0 = time.time()
        
        if self.sim:
            self.kickoff_status = DeviceStatus(self)
            self.kickoff_status._finished(success=True)
            
            def sim_worker():
                sleep(self.sim)
                self.complete_status._finished(success=True)
                
            threading.Thread(target=sim_worker, daemon=True).start()
            return self.kickoff_status
        
        else:
            return status
    
    def complete(self):
        """
        Wait for flying to be complete, get the status object that will tell us when we are done
        """

        def check_value(*,old_value, value, **kwargs):
            #Return True when the acquisition is complete, False otherwise.   
            if not self._acquiring:  #But only report done if acquisition was already started 
                return False
            return (value != 0)

        if self.complete_status is None:
            raise RuntimeError("No collection in progress")
        
        if self.sim:
            
            pass
            
        else:
            self.complete_status = SubscriptionStatus(self.done,check_value)
            
        return self.complete_status
        
    
    
    def describe_collect(self):
        """
        Describe details for ``collect()`` method
        
        fetch the file once and sniff the header to find out the data structure
        https://nsls-ii.github.io/bluesky/event_descriptors.html
        """
        #Open the file and peak inside:
        print("describing data format")
        
        #get the most recent .mpr file from the directory
        filename = self.latest_mpr_file()
        mprs=BL.MPRfile(filename) #--import MPR file with galvani\n",
        dfs=pd.DataFrame(mprs.data) #--change mpr file to data frame\n",
        

        #column names
        item_names = list(dfs.columns)
        
        item_units = []
        for item in dfs.columns:
            if "/" in item:
                item_units.append(item.split('/')[1])
            else:
                item_units.append("")
                
                
        num_items = len(item_names)

        return_dict = {self.name:{}}
        
        for key in item_names:
            format_name = key.replace(" ","_")
            if "/" in format_name:
                split = format_name.split('/')
                format_name = split[0]
                units = split[1]
                
            else:
                units = ""
                
            return_dict[self.name][f'{self.name}_{format_name}'] = {'source': f'{self.name}_{format_name}',
                                                                    'dtype': 'number',
                                                                    'units': units,
                                                                    'shape': []}
            

        
        return return_dict
        
        
    def latest_mpr_file(self):
        
        """
        returns the name of the latest mpr file in the data directory, searched recursively
        """
        


        list_of_mpr_files = []

        for path in Path(self.data_dir).rglob("*.mpr"):
            list_of_mpr_files.append(path.resolve())
    

        latest_file = str(max(list_of_mpr_files, key=os.path.getmtime))        
        return latest_file


    def collect(self):
        """
        fetch and parse the file
        
        """
        self.complete_status = None
        
        #get the most recent .mpr file from the directory
        filename = self.latest_mpr_file()
        mprs=BL.MPRfile(filename) #--import MPR file with galvani\n",
        dfs=pd.DataFrame(mprs.data) #--change mpr file to data frame\n",
        
        #for now we will assume it's always OCV
        item_names = list(dfs.columns)       
        data = {}
        
        for i in range(len(dfs)):
            
            epoch = self.t0 + dfs["time/s"][i]
            data_dict = {}
            timestamps_dict = {}
            for key in dfs:
                format_name = key.replace(" ","_")
                if "/" in format_name:
                    split = format_name.split('/')
                    format_name = split[0]
                    units = split[1]

                else:
                    units = ""
                
                data_dict[f'{self.name}_{format_name}'] = dfs[key][i]
                timestamps_dict[f'{self.name}_{format_name}'] = epoch
                
            d = dict(
                time=epoch,
                data=data_dict,
                timestamps=timestamps_dict
            )
            yield d
        
        
        
        
        
        
        
    


class BasicFlyer(Device):   

    def __init__(self, prefix='', *, limits=None, name=None, read_attrs=None,
                 configuration_attrs=None, parent=None, egu='', **kwargs):
        super().__init__(prefix=prefix, read_attrs=read_attrs,
                         configuration_attrs=configuration_attrs,
                         name=name, parent=parent, **kwargs)  
        self.complete_status = None
        self._acquiring = False
        self.t0 = 0
        

    def kickoff(self):
        """
        Start this Flyer, return a status object that sets finished once we have started
        """
        #logger.info("kickoff()")
        self.kickoff_status = DeviceStatus(self)
        self.complete_status = DeviceStatus(self)
        self._acquiring = True
        self.t0 = time.time()

        if self.init_cmd is not None:
            self.init_cmd.put(1)

        def check_value(*,old_value, value, **kwargs):
            #Return True when the acquisition is complete, False otherwise.   
            if not self._acquiring:  #But only report done if acquisition was already started 
                return False
            return (value != 0)
        
        wait(SubscriptionStatus(self.ready, check_value,settle_time=0.2))

        if self.start_cmd is not None:
            self.start_cmd.put(1)
        
        # once started, we notify by updating the status object
        self.kickoff_status._finished(success=True)

        return self.kickoff_status

    def pause(self):

        self.stop_cmd.put(1)

        sta = DeviceStatus(self)
        sta._finished(success=True)
        return sta

    def resume(self):

        self.start_cmd.put(1)

        sta = DeviceStatus(self)
        sta._finished(success=True)
        return sta

    def stop(self):

        self.stop_cmd.put(1)
        self.complete_status._finished(success=True)
        sta = DeviceStatus(self)
        sta._finished(success=True)
        return sta

    def complete(self):
        """
        Wait for flying to be complete, get the status object that will tell us when we are 
        """
        print("we've be asked to complete")

        def check_value(*,old_value, value, **kwargs):
            #Return True when the acquisition is complete, False otherwise.   
            if not self._acquiring:  #But only report done if acquisition was already started 
                return False
            return (value != 0)

        if self.complete_status is None:
            raise RuntimeError("No collection in progress")
        
        self.complete_status = SubscriptionStatus(self.done,check_value)
        return self.complete_status

    def collect(self):
        """
        Retrieve the data
        """
        # This is dummy data to test the formation of a list
        self.complete_status = None
        for _ in range(5):
            t = time.time()
            x = t - self.t0 
            d = dict(
                time=t,
                data={self.name+'_pos':x},
                timestamps=dict(x=t)
            )
            yield d
        
    
    def describe_collect(self):
 
        """
        Describe details for ``collect()`` method
        """
        d = dict(
            source = "elapsed time, s",
            dtype = "number",
            shape = []
        )
        return {
            self.name: {
                self.name+'_pos': d
            }
        }


class MyDetector(Device):
    
    count =  Cpt(EpicsSignalRO,'sensor4:getCount', kind='hinted') 

#models ue48_pgm.en

class MySubPositioner(PVPositioner):

    setpoint = Cpt(EpicsSignal,'axis4:setStartPos', kind='normal') 
    readback = Cpt(EpicsSignalRO,'axis4:getPos', kind='hinted') 
    actuate = Cpt(EpicsSignal, 'axis4:init.PROC', kind='config')
    done = Cpt(EpicsSignal, 'axis4:ready', kind='config')

class MyMotor(BasicFlyer):
    
    start_pos = Cpt(EpicsSignal,'axis4:setStartPos', kind='config') 
    end_pos = Cpt(EpicsSignal,'axis4:setEndPos', kind='config')
    pos = Cpt(EpicsSignalRO,'axis4:getPos', kind='hinted') 
    velocity = Cpt(EpicsSignal,'axis4:setVel', kind='config')
    start_cmd = Cpt(EpicsSignal, 'axis4:start.PROC', kind='config')
    stop_cmd = Cpt(EpicsSignal, 'axis4:stop.PROC', kind='config')
    init_cmd = Cpt(EpicsSignal, 'axis4:init.PROC', kind='config')
    done = Cpt(EpicsSignal, 'axis4:done', kind='config')
    ready = Cpt(EpicsSignal, 'axis4:ready', kind='config')
    
    sub_pos = Cpt(MySubPositioner,"",kind="config")
    
    
    def set(self,value):
    
        return self.sub_pos.set(value)
    
        
    
    read_attrs = ['pos']
    
    
        


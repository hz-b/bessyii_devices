
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
import time

class BasicFlyer(Device):   


    def __init__(self, prefix, *args, **kwargs):
        super().__init__(prefix, parent=None, **kwargs)
        self.complete_status = None
        self._acquiring = False
        self.t0 = 0
        
        
    def my_activity(self):
        """
        start the "fly scan" here, could wait for completion
        
        It's OK to use blocking calls here 
        since this is called in a separate thread
        from the Bluesky RunEngine.
        """
        
        
        
        if self.complete_status is None:
            logger.info("leaving activity() - not complete")
            return
        
        if self.init_cmd is not None:
            self.init_cmd.put(1)
        
        def check_value(*,old_value, value, **kwargs):
            #Return True when the acquisition is complete, False otherwise.   
            if not self._acquiring:  #But only report done if acquisition was already started 
                return False
            return (value != 0)
        
        wait(SubscriptionStatus(self.ready, check_value,settle_time=0.2))
        
        
        # TODO: do the activity here
        if self.start_cmd is not None:
            self.start_cmd.put(1)
        # once started, we notify by updating the status object
        self.kickoff_status._finished(success=True)

        # TODO: wait for completion
        self.complete_status = SubscriptionStatus(self.done,check_value)
        
        #logger.info("activity() complete. status = " + str(self.complete_status))

    def kickoff(self):
        """
        Start this Flyer, return a status object that sets finished once we have started
        """
        #logger.info("kickoff()")
        self.kickoff_status = DeviceStatus(self)
        self.complete_status = DeviceStatus(self)
        self._acquiring = True
        self.t0 = time.time()
        thread = threading.Thread(target=self.my_activity, daemon=True)
        thread.start()
        
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
        Wait for flying to be complete, get the status object that will tell us when we are done
        """
        #logger.info("complete()")
        if self.complete_status is None:
            raise RuntimeError("No collection in progress")

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
    
    read_attrs = ['pos']


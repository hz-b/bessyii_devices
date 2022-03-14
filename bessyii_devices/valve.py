from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO
from ophyd import Component as Cpt
from .positioners import PVPositionerDone

# This class can be used for the valves 

# prefix list U17
# V03V01U012L:


class Valve(PVPositionerDone):
    setpoint    = Cpt(EpicsSignal, 'SetTa', string='True') 
    readback    = Cpt(EpicsSignalRO, 'State1', string='True', kind='hinted', labels={"valves"}) 
    #done       = Cpt(EpicsSignalRO, '_REF_STAT' )  # where to find?
    
    done_value = 0 


from bessyii_devices.positioners import  InternalSignal
from ophyd.signal import Signal, SignalRO

class PositionerBessyValve(PVPositioner):
    """
    A class which creates setpoint, readback and done signals for the bessy valves which only have toggle and status
    
    1 is open, 0 is closed
    done is 1, moving is 0
    
    enums from status pv:
  
      [ 0] closing(----)
      [ 1] closed(---C)
      [ 2] opened(--O-)
      [ 3] error(--OC)
      [ 4] closing(-F--)
      [ 5] closed(-F-C)
      [ 6] closing(-FO-)
      [ 7] error(-FOC)
      [ 8] error(S---)
      [ 9] error(S--C)
      [10] opened(S-O-)
      [11] error(S-OC)
      [12] opening(SF--)
      [13] opening(SF-C)
      [14] opened(SFO-)
      [15] error(SFOC)

    """
    
    setpoint = Cpt(Signal)
    readback = Cpt(InternalSignal, value=0, labels={"valves"})
    
    _default_read_attrs = ['readback']
    
    toggle    = Cpt(EpicsSignal, 'SetTa') 
    status    = Cpt(EpicsSignalRO, 'State1') 
    done = Cpt(InternalSignal, value=0)
    done_value = 1
    
    moving_vals = [0,4,6,12,13]  # the values which the valve reports if it is moving
    opened_values = [2,10,14]
    closed_values = [1,5]
    error_values = [15,11,9,8,7,3]
 
    
    def _update_setpoint(self, *args, value, **kwargs):
        """Callback to update done state, and if required use toggle"""
 
        #If the value requested is different to the current position
        if value != self.readback.get():

            #Set done to 0, and start the move
            self.done.put(0, force=True)
            self.toggle.put(1)
        else:
            #Else, toggle done so that the status object completes
            self.done.put(0, force=True)
            self.done.put(1, force=True)

    
    def _update_readback_and_done(self, *args, value, **kwargs):
        """ Callback to update the readback and done based on current and previous status"""
   
        #Required for first call so that _last_status exists
        if self._last_status == None:
            self._last_status = value
        
        if value in self.error_values:
            self.readback.put(-1, force=True) # error
            self.done.put(1, force=True)
            
        #If we have transitioned from moving to opened then set opened and done
        elif value in self.opened_values and self._last_status in self.moving_vals :
            self.readback.put(1, force=True) # open
            self.done.put(1, force=True)
            
        #If we have transitioned from moving to closed then set closed and done
        elif value in self.closed_values and self._last_status in self.moving_vals:
            self.readback.put(0, force=True) # closed
            self.done.put(1, force=True)
            
        
        #Else, if the status value hasn't changed out of a moving state then done will remain 0
        
        #Record the value to find the transition
        self._last_status = value
                
    def __init__(self, prefix, *, name, **kwargs):
        self._last_status = None
        
        super().__init__(prefix, name=name, **kwargs)
        self.readback.name = self.name
        # Determine the initial state of the readback
        if self.status.get() in self.opened_values:
              self.readback.put(1, force=True) # open
        
        # For now ignore the error state. If we are moving the callbacks will find the state we are in
        else:
              self.readback.put(0, force=True) # close

        # Subscribe callbacks to changes of the status PV, or requests to change setpoint
        self.status.subscribe(self._update_readback_and_done, event_type=Signal.SUB_VALUE, run=False)
        self.setpoint.subscribe(self._update_setpoint, event_type=Signal.SUB_VALUE, run=False)
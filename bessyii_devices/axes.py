from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device
from ophyd.signal import Signal, SignalRO
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt
from .positioners import PVPositionerComparator



# Used only for M1 uses Software done signal
class M1Axis(PVPositionerComparator):

    setpoint    = FCpt(EpicsSignal,    '{self.prefix}{self._ch_name}Abs'              )                   
    readback    = FCpt(EpicsSignalRO,  '{self.prefix}rd{self._ch_name}', kind='hinted')

            
    atol = 1.0  # tolerance before we set done to be 1 (in um) we should check what this should be!


    def done_comparator(self, readback, setpoint):
        return setpoint-self.atol < readback < setpoint+self.atol
        
        
    def __init__(self, prefix, ch_name=None, **kwargs):
        self._ch_name = ch_name
        super().__init__(prefix, **kwargs)

# Used for hexapods
class HexapodAxis(PVPositioner):

    setpoint = FCpt(EpicsSignal,    '{self.prefix}hexapod:setPose{self._ch_name}'                   )                   
    readback = FCpt(EpicsSignalRO,  '{self.prefix}hexapod:getReadPose{self._ch_name}', kind='hinted')
    done     = Cpt(EpicsSignalRO,   'multiaxis:running'                                     )
    
    done_value = 0
    def __init__(self, prefix, ch_name=None, **kwargs):
        self._ch_name = ch_name
        super().__init__(prefix, **kwargs)
        

# Used on AU1, AU3, PINK and Pinhole        
class AxisTypeA(PVPositionerComparator):

    setpoint = FCpt(EpicsSignal,    '{self.prefix}Abs{self._ch_name}'                 )                   
    readback = FCpt(EpicsSignalRO,  '{self.prefix}rdPos{self._ch_name}', kind='hinted')
    #done     = FCpt(EpicsSignalRO,  '{self.prefix}State{self._ch_name}'               )
    
    # For combined movements
   
    # done_value = 0          #Need to test this
    atol = 0.005  # tolerance before we set done to be 1 (in um) we should check what this should be!

    def done_comparator(self, readback, setpoint):
        return setpoint-self.atol < readback < setpoint+self.atol
    
    def __init__(self, prefix, ch_name=None, **kwargs):
        self._ch_name = ch_name
        super().__init__(prefix, **kwargs)

# For combined movements AU1, AU3 PINK and Pinhole    
class AxisTypeAGap(PVPositionerComparator):

    move_gap = FCpt(EpicsSignal,    '{self.prefix}cmdGap{self._ch_name}'              ) 
    readback = FCpt(EpicsSignalRO,  '{self.prefix}rdPos{self._ch_name}', kind='hinted')
    #done     = FCpt(EpicsSignalRO,  '{self.prefix}State{self._ch_name}'               )
    
    # done_value = 0          #Need to test this
    atol = 0.005  # tolerance before we set done to be 1 (in um) we should check what this should be!

    def done_comparator(self, readback, move_gap):
        return move_gap-self.atol < readback < move_gap+self.atol
    
    def __init__(self, prefix, ch_name=None, **kwargs):
        self._ch_name = ch_name
        super().__init__(prefix, **kwargs)      
        
        
        
# Used on AU2 and Diamond Filter        
class AxisTypeB(PVPositionerComparator):

    setpoint = Cpt(EpicsSignal,    '_SET'              )                 
    readback = Cpt(EpicsSignalRO,  '_GET',kind='hinted')
    #done     = Cpt(EpicsSignalRO,  '_REF_STAT'             )
    
    #done_value = 0 
    atol = 0.005  # tolerance before we set done to be 1 (in um) we should check what this should be!

    def done_comparator(self, readback, setpoint):
        return setpoint-self.atol < readback < setpoint+self.atol
    
    def __init__(self, prefix, ch_name=None, **kwargs):
        self._ch_name = ch_name
        super().__init__(prefix, **kwargs)

# For combined movements AU2 and Diamond Filter   
class AxisTypeBGap(PVPositionerComparator):

    move_gap = FCpt(EpicsSignal,    '{self.prefix}cmdGap{self._ch_name}'            )    
    readback = FCpt(EpicsSignalRO,  '{self.prefix}_GET{self._ch_name}', kind='hinted')           
    #done     = Cpt(EpicsSignalRO,  '_REF_STAT'             )
    
    #done_value = 0 
    atol = 0.005  # tolerance before we set done to be 1 (in um) we should check what this should be!

    def done_comparator(self, readback, move_gap):
        return move_gap-self.atol < readback < move_gap+self.atol
    
    def __init__(self, prefix, ch_name=None, **kwargs):
        self._ch_name = ch_name
        super().__init__(prefix, **kwargs)

   

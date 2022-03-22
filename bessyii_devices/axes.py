from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device
from ophyd.signal import Signal, SignalRO
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt
from ophyd import Kind
from .positioners import PVPositionerComparator


# Used only for M1 uses Software done signal
class M1Axis(PVPositionerComparator):

    setpoint    = FCpt(EpicsSignal,    '{self.prefix}{self._ch_name}Abs', kind='config' )
    readback    = FCpt(EpicsSignalRO,  '{self.prefix}rd{self._ch_name}', kind='hinted')


    atol = 1.0  # tolerance before we set done to be 1 (in um) we should check what this should be!


    def done_comparator(self, readback, setpoint):
        return setpoint-self.atol < readback < setpoint+self.atol


    def __init__(self, prefix, ch_name=None, **kwargs):
        self._ch_name = ch_name
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name


# Used only for M1 uses Software done signal
class M1AxisAquarius(PVPositionerComparator):

    setpoint = FCpt(EpicsSignal, '{self.prefix}.VAL', kind='config'  ) 
    stop_setpoint = FCpt(EpicsSignal, '{self.prefix}.STOP', kind='config'  )      
    setpoint_relative = FCpt(EpicsSignal, '{self.prefix}.TWV', kind='config' )                  
    readback = FCpt(EpicsSignalRO, '{self.prefix}.RBV', kind='hinted')

            
    atol = 1.0  # tolerance before we set done to be 1 (in um) we should check what this should be!


    def done_comparator(self, readback, setpoint):
        return setpoint-self.atol < readback < setpoint+self.atol
        
        
    def __init__(self, prefix, ch_name=None, **kwargs):
        self._ch_name = ch_name
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name


# Used for hexapods
class HexapodAxis(PVPositioner):

    setpoint = FCpt(EpicsSignal,    '{self.prefix}hexapod:setPose{self._ch_name}', kind='config'   )
    readback = FCpt(EpicsSignalRO,  '{self.prefix}hexapod:getReadPose{self._ch_name}', kind='hinted')
    done     = Cpt(EpicsSignalRO,   'multiaxis:running' , kind='config'         )
    
    done_value = 0
    def __init__(self, prefix, ch_name=None, **kwargs):
        self._ch_name = ch_name
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name 

# EMIL
# Used on AU1, AU3 and Pinhole

class AxisTypeA(PVPositioner):

    setpoint = FCpt(EpicsSignal,    '{self.prefix}Abs{self._ch_name}',kind='hinted')
    readback = FCpt(EpicsSignalRO,  '{self.prefix}rdPos{self._ch_name}', kind='hinted')
    done = FCpt(EpicsSignalRO,  '{self.prefix}State{self._ch_name}',kind='normal')

    def __init__(self, prefix, ch_name=None, **kwargs):
        self._ch_name = ch_name
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name

# Used on AU2 and Diamond Filter        
class AxisTypeB(PVPositioner):

    setpoint = Cpt(EpicsSignal,    '_SET',kind='hinted'              )
    readback = Cpt(EpicsSignalRO,  '_GET',kind='hinted')
    done     = Cpt(EpicsSignalRO,  '_STATUS')
    
    done_value = 0 
    
    def __init__(self, prefix, ch_name=None, **kwargs):
        self._ch_name = ch_name
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name 

# Aquarius
#Set			AUYU15L:Top.VAL
#Set range		AUYU15L:Top.TWV
#Status 			AUYU15L:Top.STOP
#Stop			AUYU15L:Top.stMotor

class AxisTypeC(PVPositionerComparator):

    setpoint = FCpt(EpicsSignal,    '{self.prefix}.VAL{self._ch_name}', kind='config' )                   
    readback = FCpt(EpicsSignalRO,  '{self.prefix}.RBV{self._ch_name}', kind='hinted')
    #done     = FCpt(EpicsSignalRO,  '{self.prefix}State{self._ch_name}'               )
    
   # done_value = 0          #Need to test this
    atol = 0.005  # tolerance before we set done to be 1 (in um) we should check what this should be!

    def done_comparator(self, readback, setpoint):
        return setpoint-self.atol < readback < setpoint+self.atol
    
    def __init__(self, prefix, ch_name=None, **kwargs):
        self._ch_name = ch_name
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name
        
class AxisTypeD(PVPositionerComparator):

    setpoint = FCpt(EpicsSignal,    '{self.prefix}.VAL', kind='config')
    readback = FCpt(EpicsSignalRO,  '{self.prefix}.RBV', kind='hinted')
    #done     = FCpt(EpicsSignalRO,  '{self.prefix}State{self._ch_name}'               )
    
   # done_value = 0          #Need to test this
    atol = 0.005  # tolerance before we set done to be 1 (in um) we should check what this should>

    def done_comparator(self, readback, setpoint):
        return setpoint-self.atol < readback < setpoint+self.atol
    
    def __init__(self, prefix, ch_name=None, **kwargs):
        self._ch_name = ch_name
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name 

class AxisTypeFoil(PVPositionerComparator):

    setpoint = FCpt(EpicsSignal,    '{self.prefix}_SET{self._ch_name}', kind='config')                   
    readback = FCpt(EpicsSignalRO,  '{self.prefix}_GET{self._ch_name}', kind='hinted')

    atol = 0.005  # tolerance before we set done to be 1 (in um) we should check what this should be!

    def done_comparator(self, readback, setpoint):
        return setpoint-self.atol < readback < setpoint+self.atol
    
    def __init__(self, prefix, ch_name=None, **kwargs):
        self._ch_name = ch_name
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name 

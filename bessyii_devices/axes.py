from ophyd import EpicsSignal, EpicsSignalRO
from ophyd.signal import Signal, SignalRO
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt
from ophyd import Kind
from .positioners import PVPositionerComparator, PVPositionerBessy
from .device import  Device

# Used only for M1 uses Software done signal
class M1Axis(PVPositionerBessy):

    setpoint    = FCpt(EpicsSignal,    '{self.prefix}{self._ch_name}Abs', kind='normal' )
    readback    = FCpt(EpicsSignalRO,  '{self.prefix}rd{self._ch_name}', kind='hinted')
    done = FCpt(EpicsSignalRO,  '{self.prefix}ExecSens', kind='omitted')
    done_value = 0

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
class HexapodAxis(PVPositionerBessy):

    setpoint = FCpt(EpicsSignal,   '{self.prefix}hexapod:getPose{self._ch_name}', write_pv = '{self.prefix}hexapod:setPose{self._ch_name}', kind='normal'   )
    readback = FCpt(EpicsSignalRO,  '{self.prefix}hexapod:getReadPose{self._ch_name}', kind='hinted')
    done     = Cpt(EpicsSignalRO,   'multiaxis:running' , kind='omitted'         )
    
    done_value = 0
    def __init__(self, prefix, ch_name=None, **kwargs):
        self._ch_name = ch_name
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name 

# EMIL
# Used on AU1, AU3 and Pinhole

class AxisTypeA(PVPositionerBessy):

    setpoint = FCpt(EpicsSignal,    '{self.prefix}Abs{self._ch_name}',kind='normal')
    readback = FCpt(EpicsSignalRO,  '{self.prefix}rdPos{self._ch_name}', kind='hinted')
    done = Cpt(Signal, value=True)
    done_value = True
    running_signal = FCpt(EpicsSignalRO,  '{self.prefix}Run{self._ch_name}',kind='omitted')
    velocity = FCpt(EpicsSignal,  '{self.prefix}rdSpeed{self._ch_name}', write_pv = '{self.prefix}Speed{self._ch_name}',kind='config')
    
    def cb_setpoint(self, *args, **kwargs):
        """
        Called when setpoint changes (EPICS CA monitor event).
        When the setpoint is changed, force done=False.  For any move, 
        done must go != done_value, then back to done_value (True).
        Without this response, a small move (within tolerance) will not return.
        Next update of readback will compute self.done.
        """
        self.done.put(False)

        diff = self.readback.get() - self.setpoint.get()
        dmov = abs(diff) <= self._atol

        if dmov and not self.running_signal.get():
        
            self.done.put(True)
    
    def cb_running(self, *args, **kwargs):

        self.done.put(not(self.running_signal.get()))

    

    def __init__(self, prefix, ch_name=None,atol=0.001, **kwargs):
        self._ch_name = ch_name
        self._atol = atol
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name
        self.setpoint.subscribe(self.cb_setpoint)
        self.running_signal.subscribe(self.cb_running)

# Used on AU2 and Diamond Filter        
class AxisTypeB(PVPositionerBessy):

    setpoint = Cpt(EpicsSignal,    '_SET', kind='normal')                   
    readback = Cpt(EpicsSignalRO,  '_GET', kind='hinted')
    done     = Cpt(EpicsSignalRO,  '_STATUS', kind='omitted')
    done_value = 0 
    


class AxisTypeBChoice(PVPositionerBessy):

    setpoint = Cpt(EpicsSignal,    '_GON', kind='normal')                   
    readback = Cpt(EpicsSignalRO,  '_GETN',string=True, kind='hinted')
    done     = Cpt(EpicsSignalRO,  '_STATUS', kind='omitted')
    done_value = 0 
    

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

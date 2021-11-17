from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device

from ophyd import Component as Cpt

#https://gitlab.helmholtz-berlin.de/sissy/ioc/emilel/EMIL_LOCK_00

class Lock(Device):
    
    user = Cpt(EpicsSignal, "getUser", write_pv= "setUser",string='True',kind='config')
    key = Cpt(EpicsSignalRO, "key")
    clear = Cpt(EpicsSignal, "clearName.PROC")
    free = Cpt(EpicsSignalRO, "free")
    
    def unlock(self):
        
        self.clear.put(1)
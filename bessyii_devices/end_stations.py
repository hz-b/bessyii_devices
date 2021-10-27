#OAESE Motors
from ophyd import Device, EpicsMotor
from ophyd import Component as Cpt
from .keithley import Keithley6514
from .bruker import MyEpicsMCA
from ophyd.status import AndStatus

from numpy.linalg import norm
import numpy
from ophyd.pseudopos import (pseudo_position_argument,
                             real_position_argument)
from ophyd import PseudoPositioner, PseudoSingle

class OAESE(PseudoPositioner):
    
    def __init__(self,prefix, atol=1, **kwargs):
        self.atol=atol
        super().__init__(prefix, **kwargs)
    
    x = Cpt(EpicsMotor, 'motor0:mx')
    y = Cpt(EpicsMotor, 'motor0:my')
    z = Cpt(EpicsMotor, 'motor0:mz')
    kth00 = Cpt(Keithley6514, 'Keithley00:')
    kth01 = Cpt(Keithley6514, 'Keithley01:')
    bruker = Cpt(MyEpicsMCA,'SDD00:mca1')
    
    #Pseudo Axis
    pos = Cpt(PseudoSingle, name='pos')
    
    pos_dict ={}

    #save the current position with a particular name
    def save(self, name):
        
        self.pos_dict[name]= numpy.array((self.x.user_readback.get(),
                              self.y.user_readback.get(),
                              self.z.user_readback.get()))
                            
        
    @pseudo_position_argument
    def forward(self, pseudo):
        '''Run a forward (pseudo -> real) calculation'''
        name = pseudo.pos
        print(name)

        if name in self.pos_dict:
            
            return self.RealPosition(x=self.pos_dict[name][0],
                                     y=self.pos_dict[name][1],
                                     z=self.pos_dict[name][2]                                    
                                    )
        else: 
            print("We don't know that position")
            return self.RealPosition(x=self.x.user_setpoint.get(),
                                     y=self.y.user_setpoint.get(),
                                     z=self.z.user_setpoint.get()
                                    )
             
    @real_position_argument
    def inverse(self, real):
        '''Run an inverse (real -> pseudo) calculation'''
        coord = numpy.array((real.x,
                             real.y,
                             real.z))
        for name in self.pos_dict:
            if norm(self.pos_dict[name]-coord)<self.atol:
        
                return self.PseudoPosition(pos=name)
        
        else:
            
            return self.PseudoPosition(pos="unknown")
        
        



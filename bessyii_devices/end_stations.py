from ophyd import Device, EpicsMotor, EpicsSignalRO, EpicsSignal
from ophyd import Component as Cpt
from .keithley import Keithley6514
from .bruker import Bruker
from ophyd.status import AndStatus

from numpy.linalg import norm
import numpy
from ophyd.pseudopos import (pseudo_position_argument,
                             real_position_argument)
from ophyd import PseudoPositioner, PseudoSingle


#OAESE Motors
class OAESE(PseudoPositioner):
    
    def __init__(self,prefix, atol=1, **kwargs):
        self.atol=atol
        super().__init__(prefix, **kwargs)
    
    x = Cpt(EpicsMotor, 'motor0:mx')
    y = Cpt(EpicsMotor, 'motor0:my')
    z = Cpt(EpicsMotor, 'motor0:mz')
    kth00 = Cpt(Keithley6514, 'Keithley00:')
    kth01 = Cpt(Keithley6514, 'Keithley01:')
    temp1 = Cpt(EpicsSignal,'TEMPERATURE01:getTemp', name = 'temp1',auto_monitor =True, kind ='hinted')
    temp2 = Cpt(EpicsSignal,'TEMPERATURE02:getTemp', name = 'temp2',auto_monitor =True,  kind ='hinted')
    temp3 = Cpt(EpicsSignal,'TEMPERATURE03:getTemp', name = 'temp3',auto_monitor =True,  kind ='hinted')
    temp4 = Cpt(EpicsSignal,'TEMPERATURE04:getTemp', name = 'temp4',auto_monitor =True,  kind ='hinted')
    temp5 = Cpt(EpicsSignal,'TEMPERATURE05:getTemp', name = 'temp5',auto_monitor =True,  kind ='hinted')
#    bruker = Cpt(Bruker,'SDD00:')
    
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
        
        

#METRIXS Spectrometer
class METRIXSSpectrometer(PseudoPositioner):
    
    def __init__(self,prefix, atol=1, **kwargs):
        self.atol=atol
        super().__init__(prefix, **kwargs)
    
    grating_alpha1 = Cpt(EpicsMotor, 'pmacAxis1')
    grating_alpha2 = Cpt(EpicsMotor, 'pmacAxis2')
    enc_grating_11 = Cpt(EpicsMotor, 'pmacAxisEnc1')
    enc_grating_12 = Cpt(EpicsMotor, 'pmacAxisEnc2')
    enc_grating_21 = Cpt(EpicsMotor, 'pmacAxisEnc3')
    enc_grating_22 = Cpt(EpicsMotor, 'pmacAxisEnc4')
    
    
    #Pseudo Axis
    pos = Cpt(PseudoSingle, name='pos')
    
    pos_dict ={}

    #save the current position with a particular name
    def save(self, name):
        
        self.pos_dict[name]= numpy.array((self.grating_alpha1.user_readback.get(),
                                          self.grating_alpha2.user_readback.get(),
                                          self.enc_grating_11.user_readback.get(),
                                          self.enc_grating_12.user_readback.get(),
                                          self.enc_grating_21.user_readback.get(),
                                          self.enc_grating_22.user_readback.get()
                                          ))
                            
        
    @pseudo_position_argument
    def forward(self, pseudo):
        '''Run a forward (pseudo -> real) calculation'''
        name = pseudo.pos
        print(name)

        if name in self.pos_dict:
            
            return self.RealPosition(grating_alpha1=self.pos_dict[name][0],
                                     grating_alpha2=self.pos_dict[name][1],
                                     enc_grating_11=self.pos_dict[name][2],
                                     enc_grating_12=self.pos_dict[name][3],
                                     enc_grating_21=self.pos_dict[name][4],
                                     enc_grating_22=self.pos_dict[name][5]                                     
                                    )
        else: 
            print("We don't know that position")
            return self.RealPosition(grating_alpha1=self.grating_alpha1.user_setpoint.get(),
                                     grating_alpha2=self.grating_alpha2.user_setpoint.get(),
                                     enc_grating_11=self.enc_grating_11.user_setpoint.get(),
                                     enc_grating_12=self.enc_grating_12.user_setpoint.get(),
                                     enc_grating_21=self.enc_grating_21.user_setpoint.get(),
                                     enc_grating_22=self.enc_grating_22.user_setpoint.get()
                                    )
             
    @real_position_argument
    def inverse(self, real):
        '''Run an inverse (real -> pseudo) calculation'''
        coord = numpy.array((real.grating_alpha1,
                             real.grating_alpha2,
                             real.enc_grating_11,
                             real.enc_grating_12,
                             real.enc_grating_21,
                             real.enc_grating_22
                            ))
        
        for name in self.pos_dict:
            if norm(self.pos_dict[name]-coord)<self.atol:
        
                return self.PseudoPosition(pos=name)
        
        else:
            
            return self.PseudoPosition(pos="unknown")

# METRIXS Detector Unit 
class METRIXSDetector(PseudoPositioner):
    
    def __init__(self,prefix, atol=1, **kwargs):
        self.atol=atol
        super().__init__(prefix, **kwargs)
    
    z          = Cpt(EpicsMotor, 'DetZ', labels={"detector"})
    distance   = Cpt(EpicsMotor, 'DetDist', labels={"detector"})
        
    #Pseudo Axis
    pos = Cpt(PseudoSingle, name='pos')
    
    pos_dict ={}

    #save the current position with a particular name
    def save(self, name):
        
        self.pos_dict[name]= numpy.array((self.z.user_readback.get(),
                                          self.distance.user_readback.get()
                                          ))
                            
        
    @pseudo_position_argument
    def forward(self, pseudo):
        '''Run a forward (pseudo -> real) calculation'''
        name = pseudo.pos
        print(name)

        if name in self.pos_dict:
            
            return self.RealPosition(z=self.pos_dict[name][0],
                                     distance=self.pos_dict[name][1]                                 
                                    )
        else: 
            print("We don't know that position")
            return self.RealPosition(z=self.z.user_setpoint.get(),
                                     distance=self.distance.user_setpoint.get()
                                    )
             
    @real_position_argument
    def inverse(self, real):
        '''Run an inverse (real -> pseudo) calculation'''
        coord = numpy.array((real.z,
                             real.distance
                            ))
        
        for name in self.pos_dict:
            if norm(self.pos_dict[name]-coord)<self.atol:
        
                return self.PseudoPosition(pos=name)
        
        else:
            
            return self.PseudoPosition(pos="unknown")
        

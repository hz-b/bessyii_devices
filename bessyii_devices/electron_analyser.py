from ophyd.areadetector.cam import CamBase
from ophyd.areadetector.detectors import DetectorBase

from ophyd.areadetector.base import (ADBase, ADComponent as ADCpt, ad_group,
                   EpicsSignalWithRBV as SignalWithRBV)
from ophyd.signal import (EpicsSignalRO, EpicsSignal)
from ophyd.device import DynamicDeviceComponent as DDC
from ophyd import Component as Cpt

from bessyii_devices.positioners import PVPositionerComparator
from ophyd.areadetector.base import EpicsSignalWithRBV
from ophyd.areadetector.plugins import StatsPlugin_V33, ImagePlugin_V33, HDF5Plugin_V33
from .camera_ad33 import SingleTriggerV33, TIFFPluginWithFileStore
from matplotlib.pyplot import imshow

import matplotlib.pyplot as plt
import numpy as np    
class ElectronAnalyserCamV33(CamBase):
    
    """
    Device class to connect to the camera of an SES Electron analyser
    
   """
    _default_configuration_attrs = None
    
    wait_for_plugins = Cpt(EpicsSignal, 'WaitForPlugins',
                           string=True, kind='config')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stage_sigs['wait_for_plugins'] = 'Yes'

    def ensure_nonblocking(self):
        self.stage_sigs['wait_for_plugins'] = 'Yes'
        for c in self.parent.component_names:
            cpt = getattr(self.parent, c)
            if cpt is self:
                continue
            if hasattr(cpt, 'ensure_nonblocking'):
                cpt.ensure_nonblocking()

    #Energy
    pass_energy = ADCpt(EpicsSignalWithRBV,'PASS_ENERGY',kind='config')
    low_energy = ADCpt(EpicsSignalWithRBV,'LOW_ENERGY',kind='config')
    high_energy = ADCpt(EpicsSignalWithRBV,'HIGH_ENERGY',kind='config')
    fixed_energy = ADCpt(EpicsSignalWithRBV,'CENTRE_ENERGY',kind='config')
    energy_width = Cpt(EpicsSignalRO,'ENERGY_WIDTH_RBV',kind='config')
    excitation_energy = ADCpt(EpicsSignalWithRBV,'EXCITATION_ENERGY',kind='config')
    
    #Modes
    lens_mode = ADCpt(EpicsSignalWithRBV,'LENS_MODE',kind='config')
    acq_mode = ADCpt(EpicsSignalWithRBV,'ACQ_MODE',kind='config')
    energy_mode= ADCpt(EpicsSignalWithRBV,'ENERGY_MODE',kind='config')
    det_mode = ADCpt(EpicsSignalWithRBV,'DETECTOR_MODE',kind='config')
    element_mode = ADCpt(EpicsSignalWithRBV,'ELEMENT_SET',kind='config')
    
    #Step
    frames = ADCpt(EpicsSignalWithRBV,'FRAMES',kind='config')
    step_size =  ADCpt(EpicsSignalWithRBV,'STEP_SIZE',kind='config')
    slices = ADCpt(EpicsSignalWithRBV,'SLICES',kind='config')

    
class ElectronAnalyserDetector(DetectorBase):
    """
    
    AreaDetector Device for SES Analyser
    
    instantiate like this: 
    ea = ElectronAnalyserDetectorV33('RODEV:SES:', name = 'ea')
    ea.wait_for_connection()
    """
    
    _default_read_attrs = None
    cam = Cpt(ElectronAnalyserCamV33, 'CTRL:',kind='config')
    
    #spectrum
    spectrum = Cpt(EpicsSignalRO,'CTRL:INT_SPECTRUM',kind='normal')
    image = Cpt(EpicsSignalRO,'CTRL:IMAGE',kind='normal')


    

class ElectronAnalyserDetectorV33(SingleTriggerV33,ElectronAnalyserDetector):
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cam.ensure_nonblocking()
        

    
def plot_ea_image( run, idx =0):
    
    """
    
    Plot an image from an SES electron analyser given a run an index
    
    run: bluesky run from db like db[-1]
    
    idx: int
    The index within that run to plot if there are many, default 0
    
    """
    data = run.primary.read()
    image_array = data['ea_image'][idx].values
    config = run.primary.config['ea'].read()

   
    num=idx
    slices = config["ea_cam_slices"][num].values
    width = config["ea_cam_energy_width"][num].values
    step = config["ea_cam_step_size"][num].values
    high= config["ea_cam_high_energy"][num].values
    low = config["ea_cam_low_energy"][num].values

    num_regions = int(width/step) +1

    energy_vector = np.linspace(low,high+step,num_regions)
    image = image_array.reshape(slices,num_regions)
    
    plt.figure()
    plt.rcParams['figure.figsize'] = [10, 10]
    imshow(image,interpolation='none', aspect='auto',extent=[energy_vector[0],energy_vector[-1],slices,1])
    plt.xlabel('Kinetic Energy (eV)')
    plt.ylabel('slice')
    plt.title(str(run.metadata['start']['scan_id'])+" itteration " + str(idx) +  " image")

def plot_ea_spectrum(run, idx = 0):
    
    """
    
    Plot a spectra from an SES electron analyser given a run an index
    
    run: bluesky run from db like db[-1]
    
    idx: int
    The index within that run to plot if there are many, default 0
    
    """
        
    config = run.primary.config['ea'].read()
    data = run.primary.read()
   
    num=idx
    slices = config["ea_cam_slices"][num].values
    width = config["ea_cam_energy_width"][num].values
    step = config["ea_cam_step_size"][num].values
    high= config["ea_cam_high_energy"][num].values
    low = config["ea_cam_low_energy"][num].values

    num_regions = int(width/step) +1

    energy_vector = np.linspace(low,high+step,num_regions)
    
    array = data['ea_spectrum'].values[idx]
    plt.figure()
    plt.plot(energy_vector,array)
    plt.xlabel('Kinetic Energy (Ev)')
    plt.ylabel('counts')
    plt.title(str(run.metadata['start']['scan_id'])+" itteration " + str(idx) +  " image")


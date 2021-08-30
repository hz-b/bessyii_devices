from bessyii_devices.positioners import PVPositionerComparator
from ophyd.areadetector.base import ADBase
from ophyd.areadetector import SimDetector, SimDetectorCam, SingleTrigger,  URLDetectorCam, URLDetector
from ophyd.areadetector.plugins import (
    StatsPlugin,
    ImagePlugin,
    ROIPlugin,
    HDF5Plugin,
    ProcessPlugin,
    TIFFPlugin,
    ColorConvPlugin,
    TransformPlugin    
    #WarpPlugin,
)
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite, FileStoreTIFFIterativeWrite, FileStorePluginBase, FileStoreIterativeWrite
from ophyd.areadetector.base import EpicsSignalWithRBV as SignalWithRBV
from ophyd import Component as Cpt
from ophyd import EpicsSignal, EpicsSignalRO, EpicsMotor, Device, PseudoPositioner, PseudoSingle, DerivedSignal
from ophyd.pseudopos import (pseudo_position_argument,
                             real_position_argument)

from scipy.ndimage import center_of_mass
from databroker.core import SingleRunCache
from bluesky.preprocessors import subs_decorator
from bluesky.callbacks.mpl_plotting import LivePlot
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
#from poor_man_focus_chamber_def_stream import calc_FWHM
#from poor_man_focus_chamber_def import calc_FWHM_path
import time
import datetime
#from plot_proc_image import plot_FWHM_fit
#from read_image_test import read_image_test


"""
class FileStoreTIFF_mod(FileStorePluginBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filestore_spec = 'AD_TIFF'  # spec name stored in resource doc
        self.stage_sigs.update([('file_template', '%s%s_%6.6d.tiff'),
                                ('file_write_mode', 'Single'),
                                ])
        # 'Single' file_write_mode means one image : one file.
        # It does NOT mean that 'num_images' is ignored.

    def get_frames_per_point(self):
        return self.parent.cam.num_images.get()

    def stage(self):
        super().stage()
        # this over-rides the behavior is the base stage
        self._fn = self._fp

        resource_kwargs = {'template': self.file_template.get(),
                           'filename': self.file_name.get(),
                           'frame_per_point': self.get_frames_per_point()}
        self._generate_resource(resource_kwargs)

class FileStoreTIFFIterativeWrite_mod(FileStoreTIFF_mod, FileStoreIterativeWrite):
    pass
"""
"""
class SimDetectorCamV33(SimDetectorCam):
    '''This is used to update the SimDetectorCam to AD33.'''

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
    
    file_number = Cpt(SignalWithRBV, 'FileNumber')


class SimDetector(SimDetector):
    cam = Cpt(SimDetectorCamV33, 'cam1:')
"""
    
class HDF5PluginWithFileStore(HDF5Plugin, FileStoreHDF5IterativeWrite):
    pass

class TIFFPluginWithFileStore(TIFFPlugin, FileStoreTIFFIterativeWrite):
      pass  
  
    
    
class DetectorStream(SingleTrigger, URLDetector):
        
    image = Cpt(ImagePlugin, 'image1:')
    cam = Cpt(URLDetectorCam, 'cam1:')
    transform_type = 0
    #hdf5 = Component(HDF5PluginWithFileStore, 'HDF1:',
    #         write_path_template='/data/images/',
    #         read_path_template='/home/jovyan/images',
    #         read_attrs=[],
    #         root='/')
    
    stats = Cpt(StatsPlugin, 'Stats1:')
    colour = Cpt(ColorConvPlugin, 'CC1:')
    trans = Cpt(TransformPlugin, 'Trans1:')
    # gives the angle between the longest axis of the spot with respect to the horizontal line (horizon) 
    # Orientation = EpicsSignal('SISSY1EX:Simdetector1:Stats1:Orientation_RBV', name= 'Orientation')   
"""    # stream_image_array = 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def get_orientation(self):
        return self.Orientation.get()
    
    def get_image_array(self):
        #print(f'image array:\n {self.image.image}')
        orientation_angle_in = self.Orientation.get()
        time, vFWHM, hFWHM = calc_FWHM(self.image.image, 'steam_image', orientation_angle_in)
        plot_FWHM_fit(self.image.image)
        return time, vFWHM, hFWHM
    
    def process_image_static_path(self):
        path = './images/'
        calc_FWHM_path(path, path)
    
    def get_image_array_sum(self):
        #varibale_out = read_image_test(self.image.image)
        return read_image_test(self.image.image)
        #print(f'image array:\n {self.image.image}')        
        #calc_FWHM(self.image.image, 'image_self')
        #plot_FWHM_fit(self.image.image)
        #return self.image.image
    
    def collect_asset_image(self):
        yield from self.image.image.collect_asset_image()
    
    def show_image_array(self):
        return self.image.image
    
    def show_array_and_image(self):
        #a, b, c = plot_FWHM_fit(self.image.image)
        a, b = plot_FWHM_fit(self.image.image)
        return a, b
    
    def plot_image_array(self):
        plot_FWHM_fit(self.image.image)

        
    def statistics_test_cal(self):
        return self.stats.sigma_x.get() + 100
"""   
    #def collect_asset_docs(self):
    #    yield from []
    #warp1 = Component(WarpPlugin, 'warp1:')
    #stats2 = Component(StatsPlugin, 'Stats2:')
    
    #stats3 = Component(StatsPlugin, 'Stats3:')
    #stats4 = ComponentPlugin, 'ROI1:')
    #roi2 = Component(ROIPlugin, 'ROI2:')
    #roi3 = Component(ROIPlugin, 'ROI3:')
    #roi4 = Component(ROIPlu(StatsPlugin, 'Stats4:')
    #stats5 = Component(StatsPlugin, 'Stats5:')
    #roi1 = Component(ROIgin, 'ROI4:')
    #proc1 = Component(ProcessPlugin, 'Proc1:')


class DetectorTiff(DetectorStream, SingleTrigger, URLDetector):
        tiff = Cpt(TIFFPluginWithFileStore,
           suffix="TIFF1:",        
           write_path_template="/home/emil/Apps/autosave/images/"        
           )

        
class ScaleSignal(DerivedSignal):    
    #the init is important for input values
    def __init__(self, *args, factor, **kwargs):
        self.scaling_factor = factor
        super().__init__(*args, **kwargs) 
    
    def inverse(self, value):
        return value*self.scaling_factor   
    
   # def forward(self, value):
   #     return value / self.scaling_factor
    

class reshape_image_array_to_matrix(DerivedSignal):
    #the init is important for input values
    def __init__(self, *args, DimX, DimY, **kwargs):
        self.DimX_use = DimX
        self.DimY_use = DimY
        super().__init__(*args, **kwargs) 
    
    def inverse(self, value):
        return np.reshape(value, (self.DimX_use, self.DimY_use)) #np.reshape(array_image_from_sim, (1024, 1024))
    

class calcFWHM_by_script(DerivedSignal):    
    #the init is important for input values
    def __init__(self, *args, DimX, DimY, orientation_angle, **kwargs):
        self.DimX_use = DimX
        self.DimY_use = DimY
        self.orientation_angle_use = orientation_angle
        super().__init__(*args, **kwargs) 
    
    def inverse(self, value):
        time, vFWHM, hFWHM = calc_FWHM(np.reshape(value, (self.DimX_use, self.DimY_use)), 'steam_image', self.orientation_angle_use)  
        # when return is used, the execution starts and never ends....
   #     return time, vFWHM, hFWHM  
    
class MySimCamSigmaX(PVPositionerComparator):
    
    setpoint = Cpt(EpicsSignal, 'cam1:PeakWidthX')
    readback = Cpt(EpicsSignalRO, 'cam1:PeakWidthX_RBV')
    
    atol = 0.1
    
    def done_comparator(self, readback, setpoint):
        return setpoint-self.atol < readback < setpoint+self.atol
    
class MySimCamSigmaY(PVPositionerComparator):
    
    setpoint = Cpt(EpicsSignal, 'cam1:PeakWidthY')
    readback = Cpt(EpicsSignalRO, 'cam1:PeakWidthY_RBV')
    
    atol = 0.1
    
    def done_comparator(self, readback, setpoint):
        return setpoint-self.atol < readback < setpoint+self.atol

class SetImageBkgThreshold(PVPositionerComparator):
    
    setpoint = Cpt(EpicsSignal, 'Stats1:BgdWidth')
    readback = Cpt(EpicsSignalRO, 'Stats1:BgdWidth_RBV')
    
    atol = 0.1
    
    def done_comparator(self, readback, setpoint):
        return setpoint-self.atol < readback < setpoint+self.atol
        
class SetCentroidThreshold(PVPositionerComparator):
    
    setpoint = Cpt(EpicsSignal, 'Stats1:CentroidThreshold')
    readback = Cpt(EpicsSignalRO, 'Stats1:CentroidThreshold_RBV')
    
    atol = 0.1
    
    def done_comparator(self, readback, setpoint):
        return setpoint-self.atol < readback < setpoint+self.atol        
        
# the signals   
class DetectorStreamSignals(DetectorStream):
    #PV list: 
    # its an array that need to be reshaped as a matrix !
    stream_image_array = Cpt(EpicsSignalRO,'image1:ArrayData', name= 'singal_image') 
    
    # center of mass
    cm_x = Cpt(EpicsSignalRO,'Stats1:MaxX_RBV', name= 'cm_x', kind = 'hinted') 
    cm_y = Cpt(EpicsSignalRO,'Stats1:MaxY_RBV', name= 'cm_y', kind = 'hinted') 
    
    # center of mass centroid
    cm_c_x = Cpt(EpicsSignalRO,'Stats1:CentroidX_RBV', name= 'signal_cen_x', kind = 'hinted') 
    cm_c_y = Cpt(EpicsSignalRO,'Stats1:CentroidY_RBV', name= 'signal_cen_y', kind = 'hinted') 
    # PV list: 
    Max_Intensity = Cpt(EpicsSignalRO,'Stats1:MaxValue_RBV', name= 'signal_peak_maximum_counts', kind = 'hinted')  
    #MaxCounts = Cpt(EpicsSignalRO,'Stats1:CentroidTotal_RBV', name= 'signal_centroid_total', kind = 'hinted')  
    orientation = Cpt(EpicsSignalRO,'Stats1:Orientation_RBV', name= 'signal_orientation', kind = 'hinted') 
    spot_sigma_x = Cpt(EpicsSignalRO,'Stats1:SigmaX_RBV', name= 'signal_sigma_x', kind = 'hinted') 
    spot_sigma_y = Cpt(EpicsSignalRO,'Stats1:SigmaY_RBV', name= 'signal_sigma_y', kind = 'hinted') 
    
    # PV list: https://areadetector.github.io/master/ADSimDetector/simDetector.html?highlight=adbase 
    spot_width = Cpt(EpicsSignalRO,'cam1:PeakWidthX_RBV', name= 'signal_spot_width') 
    spot_height = Cpt(EpicsSignalRO,'cam1:PeakWidthY_RBV', name= 'signal_spot_height') 

  
    # Calculate the FWHM 
    FWHM_scaling_factor = 2.355
    #FWHM_sigma_x
    FWHM_x = Cpt(ScaleSignal, derived_from="spot_sigma_x", factor=FWHM_scaling_factor, kind="hinted")
    #FWHM_sigma_y
    FWHM_y = Cpt(ScaleSignal, derived_from="spot_sigma_y", factor=FWHM_scaling_factor, kind="hinted")
    
    # needs to be connected in IOC
    #FWHM_width = Cpt(ScaleSignal, derived_from="spot_width",  factor=FWHM_scaling_factor, kind="hinted")
    #FWHM_height = Cpt(ScaleSignal, derived_from="spot_height", factor=FWHM_scaling_factor, kind="hinted")
    
    #Reshaped_image =  Cpt(reshape_image_array_to_matrix, derived_from="stream_image_array", DimX=1024, DimY = 1024, kind="hinted")
    #Analyse_image =  Cpt(calcFWHM_by_script, derived_from="stream_image_array", DimX=1280, DimY = 720, orientation_angle = orientation, kind="hinted")  
    
        
    #BgdWidth BgdWidth_RBV
    #CentroidThreshold CentroidThreshold_RBV
    
class DetectorTiffSignals(DetectorStreamSignals, DetectorStream): 
     tiff = Cpt(TIFFPluginWithFileStore,
           suffix="TIFF1:",        
           write_path_template="/home/emil/Apps/autosave/images/"        
           )
        
def set_detector_tiff(det):
    #det.FWHM_x.kind = 'hinted'
    #det.FWHM_y.kind = 'hinted'
    #det.cm_x.kind = 'hinted'
    #det.cm_y.kind = 'hinted'
    
    #det.tiff.kind = 'normal' 
    #det.stats.kind = 'hinted'
    #det.colour.kind = 'normal'
    #det.image.kind = 'hinted'
    det.stats.total.kind = 'hinted'
    #det.stats.centroid.x.kind = 'hinted' 
    #det.stats.centroid.y.kind = 'hinted' 
    #det.cam.ensure_nonblocking()
    det.tiff.nd_array_port.put(det.colour.port_name.get()) # makes the tiff plugin take the output of the colour change plugin
    det.stats.nd_array_port.put(det.colour.port_name.get())
    det.trans.nd_array_port.put(det.colour.port_name.get())
    
def set_detector_stream(det):
    det.stats.kind = 'hinted'
    det.colour.kind = 'normal'
    det.image.kind = 'hinted'
    det.stats.sigma_x.kind = 'hinted'
    det.stats.sigma_y.kind = 'hinted'
    det.stats.sigma_xy.kind = 'hinted'
    #det.stats.sigma_xy.kind = 'hinted'
    #det.stats.skewness_x.kind = 'hinted'
    det.stats.total.kind = 'hinted'
    det.stats.centroid.x.kind = 'hinted' 
    det.stats.centroid.y.kind = 'hinted' 
    det.stats.nd_array_port.put(det.colour.port_name.get())
    det.trans.nd_array_port.put(det.colour.port_name.get())

    
def set_detector_stream_Signals(det):
    #det.spot_sigma_x.kind = 'hinted'
    #det.spot_sigma_y.kind = 'hinted'
    det.FWHM_x.kind = 'hinted'
    det.FWHM_y.kind = 'hinted'
    det.cm_x.kind = 'hinted'
    det.cm_y.kind = 'hinted'
    
    #det.FWHM_width.kind = 'hinted'
    #det.FWHM_height.kind = 'hinted'
    #det.centroid_total.kind = 'hinted'
    
    det.MaxCounts.kind = 'hinted' 
    det.orientation.kind = 'hinted' 
    #det.spot_width.kind = 'hinted'
    #det.spot_height.kind = 'hinted'
    #det.FWHM_sigma_x.kind = 'hinted'
    #det.FWHM_sigma_x.kind = 'hinted'

    det.stats.nd_array_port.put(det.colour.port_name.get())
    det.trans.nd_array_port.put(det.colour.port_name.get())
    
def set_detector_tiff_Signals(det):
    #det.spot_sigma_x.kind = 'hinted'
    #det.spot_sigma_y.kind = 'hinted'
    det.FWHM_x.kind = 'hinted'
    det.FWHM_y.kind = 'hinted'
    det.cm_x.kind = 'hinted'
    det.cm_y.kind = 'hinted'
    det.cm_c_x.kind = 'hinted'
    det.cm_c_y.kind = 'hinted'
    
    #det.FWHM_width.kind = 'hinted'
    #det.FWHM_height.kind = 'hinted'
    #det.centroid_total.kind = 'hinted'
    
    det.Max_Intensity.kind = 'hinted' 
    det.orientation.kind = 'hinted' 
    #det.spot_width.kind = 'hinted'
    #det.spot_height.kind = 'hinted'
    #det.FWHM_sigma_x.kind = 'hinted'
    #det.FWHM_sigma_x.kind = 'hinted'

    det.tiff.nd_array_port.put(det.colour.port_name.get()) # makes the tiff plugin take the output of the colour change plugin
    det.stats.nd_array_port.put(det.colour.port_name.get())
    det.trans.nd_array_port.put(det.colour.port_name.get())
    
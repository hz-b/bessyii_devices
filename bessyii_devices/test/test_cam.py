#test for cameras
import pytest
from bluesky import RunEngine
import os
import bessyii_devices
from bessyii_devices.camera_ad33 import MySimDetectorV33, MyGreateyesDetectorV33
from databroker.v2 import temp
from bluesky.plans import count,scan
from datetime import datetime, timezone
import numpy as np
from emiltools.publisher import NXWriterBESSY
from ophyd.sim import motor,noisy_det
import time
import h5py

# Sim Cam
sim_cam = MySimDetectorV33('SISSY1EX:Simdetector1:', name = 'sim_cam')
sim_cam.wait_for_connection()
sim_cam.set_detector()
sim_cam.stats.total.kind = 'hinted'
sim_cam.stats.read_attrs.append('total')

#Great Eyes CCD
hits = MyGreateyesDetectorV33('13GE1:', name = 'hits')
hits.wait_for_connection()
hits.set_detector()

def v33_check(cam):
    
    if 'wait_for_plugins' in cam.cam.stage_sigs:
        return True
    else:
        return False
    
    
def take_image_check(cam):
    # Since we are using the hdf5 file writer, this test also tests that that works!
    RE = RunEngine({})
    db = temp()
    RE.subscribe(db.v1.insert)
    
    RE(count([cam]))
    
    
    run = db[-1]
    data = run.primary.read()
    image = data[cam.name+'_image']
    frame=np.squeeze(image[0])
    db_imarray = np.array(frame)
    
    x = cam.cam.array_size.read()[cam.name+'_cam_array_size_array_size_x']['value']
    y = cam.cam.array_size.read()[cam.name+'_cam_array_size_array_size_y']['value']
   
    return db_imarray.shape == (y,x)
 
def file_export_check(cam):
    
    #test that images generated from the camera can be recovered from the nexus file written at export
    RE = RunEngine({})
    db = temp()
    RE.subscribe(db.v1.insert)
    
    nxwriter = NXWriterBESSY()
    file_path = os.path.join(os.getcwd(),'test')
    nxwriter.file_path = file_path
    #RE.subscribe(nxwriter.receiver) DO NOT subscribe it, must be run in a proxy
    
    num_points = 2
    RE(scan([cam],motor,-1,1,num_points),sample={'name':'test_sample', 'sample_id':1234,'description':'my awesome test sample','type':'sample+can', 'chemical_formula':'ABC','situation':'vacuum'},user_name='test_user',user_profile='test_user_profile')

    run = db[-1]
    nxwriter.export_run(run) # equivalent to running in a proxy
    
    #Once it's complete check that a file exists under
    uid = db[-1].metadata['start']['uid']
    scan_id = db[-1].metadata['start']['scan_id']
    date_string = datetime.now().strftime('%Y_%m_%d')
    fname = f"{scan_id:05d}"
    fname += f"_{uid[:7]}.hdf"
    file = os.path.join(nxwriter.file_path,date_string,'nx',fname)
    
    #Does it contain a 4x1024x1024 array?
    f = h5py.File(file, 'r')
    x = cam.cam.array_size.read()[cam.name+'_cam_array_size_array_size_x']['value']
    y = cam.cam.array_size.read()[cam.name+'_cam_array_size_array_size_y']['value']
    
    return (num_points, y, x) == np.shape(f['entry']['data'][cam.name+'_image'][()])

##
def check_hits_temp_controller(hits):
    
    current_temp = hits.cam.temp_control.readback.get()
    new_temp = current_temp + 1.0
    hits.cam.temp_control.move(new_temp,wait=True)
    
    return hits.cam.temp_control.readback.get() == new_temp

### Perform tests
    
def test_sim_cam_v33():
    assert v33_check(sim_cam) == True
    
def test_sim_cam_image():
    assert take_image_check(sim_cam) == True
    
def test_sim_cam_file_export():
    assert file_export_check(sim_cam) == True
    
    
def test_hits_v33():
    assert v33_check(hits) == True

# This works
#def test_hits_temp_control_exist():
#    assert isinstance(hits.cam.temp_control, PVPositionerComparator)

def test_hits_temp_control_authority():
    assert check_hits_temp_controller(hits) == True
    
def test_hits_image():
    assert take_image_check(hits) == True
    
def test_hits_file_export():
    assert file_export_check(hits) == True
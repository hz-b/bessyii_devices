from bessyii_devices.m3_m4_mirrors import SMUUE52SGM
import time

smu = SMUUE52SGM("SMUYU109L", name='SMUUE52SGM')
time.sleep(2)
print(smu.connected)
#test for oease end station
import pytest
import bessyii_devices
from bessyii_devices.lock import Lock

ue48_lock = Lock("EMILEL:LOCK00:UE48:",name="ue48_lock")
u17_lock = Lock("EMILEL:LOCK00:U17:",name="u17_lock")

ue48_lock.wait_for_connection()
u17_lock.wait_for_connection()


def lock_check(lock):
    
    lock.unlock()
    lock.user.set("test")
    
    return lock.free.get() == False

def locked_check(lock):
    
    lock.unlock()
    lock.user.set("test").wait(5)
    lock.user.put("not_test")
    
    return lock.user.get() == "test"

def unlock_check(lock):
    
    lock.unlock()
    lock.user.set("test").wait(5)
    lock.unlock()
    
    lock.user.put("not_test")
    
    return lock.user.get() == "not_test"

def test_connection_ue48():
    assert ue48_lock.connected == True
    
def test_connection_u17():
    assert u17_lock.connected == True
    
def test_lock():
    
    assert lock_check(ue48_lock) == True
    
def test_locked():
    
    assert locked_check(ue48_lock) == True
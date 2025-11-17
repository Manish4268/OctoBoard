import threading
from os import path
from .constants import SIMULATION_MODE

if SIMULATION_MODE:
    from .mock_hardware import MockI2C as I2C, MockBlinka_I2C as _I2C
else:
    from busio import I2C
    from adafruit_blinka.microcontroller.generic_linux.i2c import I2C as _I2C


class ExtendedI2C(I2C):
    """Extended I2C is a busio extension that allows creating a compatible
    I2C object using the Bus ID number. The bus ID is the number at the end
    of /dev/i2c-# and you can find which I2C devices you have by typing
    ``ls /dev/i2c*``"""

    def __init__(self, bus_id, frequency=400000):
        self._i2c = None
        self._lock = None
        self.init(bus_id, frequency)
    
    def init(self, bus_id, frequency):
        if hasattr(self, '_i2c') and self._i2c is not None:
            self.deinit()

        if not SIMULATION_MODE:
            # Check if the file /dev/i2c-{bus_id} exists and error if not
            if not path.exists(f"/dev/i2c-{bus_id}"):
                raise ValueError(f"No device found for /dev/i2c-{bus_id}")
            # Attempt to open using _I2C
            self._i2c = _I2C(bus_id, mode=_I2C.MASTER, baudrate=frequency)
        else:
            # Simulation mode - use mock I2C
            self._i2c = _I2C(bus_id, mode=1, baudrate=frequency)
        
        self._lock = threading.RLock()
        
"""
Mock hardware modules for development without Raspberry Pi.
This allows development and testing on Windows or any platform without actual hardware.
"""

import threading
import numpy as np
from datetime import datetime

# ==================== Mock busio ====================
class MockI2C:
    """Mock I2C bus for development without hardware."""
    
    def __init__(self, scl=None, sda=None, frequency=400000):
        self._lock = threading.RLock()
        self._devices = {}  # Simulated devices on the bus
        print(f"[MOCK] I2C initialized (simulated)")
    
    def try_lock(self):
        """Try to grab the lock."""
        return self._lock.acquire(blocking=False)
    
    def unlock(self):
        """Release the lock."""
        self._lock.release()
    
    def scan(self):
        """Return list of simulated I2C device addresses."""
        # Simulate 4 boards with proper address offsets
        devices = []
        for offset in range(4):
            devices.extend([
                32 + offset * 1,   # MUX
                72 + offset * 1,   # ADC
                96 + offset * 2,   # DAC_0
                97 + offset * 2,   # DAC_1
            ])
        print(f"[MOCK] I2C scan found devices: {devices}")
        return devices
    
    def writeto(self, address, buffer, start=0, end=None):
        """Mock write to I2C device."""
        pass
    
    def readfrom_into(self, address, buffer, start=0, end=None):
        """Mock read from I2C device."""
        pass


# ==================== Mock Adafruit MCP4728 (DAC) ====================
class MockMCP4728Channel:
    """Mock single channel of MCP4728 DAC."""
    
    def __init__(self):
        self._value = 0
        self._raw_value = 0
        self.gain = 1
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, val):
        self._value = val
        self._raw_value = val
    
    @property
    def raw_value(self):
        return self._raw_value


class MockMCP4728:
    """Mock MCP4728 4-channel DAC."""
    
    def __init__(self, i2c, address=0x60):
        self.address = address
        self.channel_a = MockMCP4728Channel()
        self.channel_b = MockMCP4728Channel()
        self.channel_c = MockMCP4728Channel()
        self.channel_d = MockMCP4728Channel()
        print(f"[MOCK] MCP4728 DAC initialized at address {address}")


# ==================== Mock Adafruit ADS1115 (ADC) ====================
class MockADS1115:
    """Mock ADS1115 16-bit ADC."""
    
    def __init__(self, i2c, gain=1, data_rate=128, address=0x48):
        self.address = address
        self.gain = gain
        self.data_rate = data_rate
        self.bits = 16
        self._simulated_voltage = 0.0
        self._simulated_current = 0.0
        print(f"[MOCK] ADS1115 ADC initialized at address {address}")
    
    def read(self, pin_setting):
        """Simulate ADC reading with realistic solar cell behavior."""
        # Simulate a solar cell with some variation
        # Return 16-bit integer value
        
        # Differential pairs: P0-P1 is voltage, P2-P3 is current
        if pin_setting == 0x0000:  # P0-P1 (voltage)
            # Simulate voltage reading (0-1.2V typical for solar cell)
            voltage = 0.8 + np.random.normal(0, 0.01)  # ~0.8V ± noise
            # Convert to 16-bit ADC value
            lsb = 4.096 / (1 << 15)  # For gain=1
            return int(voltage / lsb)
        
        elif pin_setting == 0x0003:  # P2-P3 (current via shunt)
            # Simulate current reading (voltage across 20Ω shunt)
            current_amps = 0.01 + np.random.normal(0, 0.0001)  # ~10mA ± noise
            voltage_across_shunt = current_amps * 20  # V = I * R
            lsb = 4.096 / (1 << 15)
            return int(voltage_across_shunt / lsb)
        
        return 0


# Mock pin settings for ADS1115
class MockPin:
    def __init__(self, value):
        self.value = value

P0 = MockPin(0)
P1 = MockPin(1)
P2 = MockPin(2)
P3 = MockPin(3)

_ADS1X15_DIFF_CHANNELS = {
    (P0, P1): 0x0000,
    (P0, P3): 0x0001,
    (P1, P3): 0x0002,
    (P2, P3): 0x0003,
}

_ADS1X15_PGA_RANGE = {
    2/3: 6.144,
    1: 4.096,
    2: 2.048,
    4: 1.024,
    8: 0.512,
    16: 0.256
}


# ==================== Mock Adafruit MCP23017 (I/O Expander) ====================
class MockMCP23017Pin:
    """Mock single pin of MCP23017."""
    
    def __init__(self, pin_num):
        self.pin_num = pin_num
        self._value = 0
    
    def switch_to_output(self, value=False):
        """Set pin as output with initial value."""
        self._value = int(value)
    
    def switch_to_input(self):
        """Set pin as input."""
        pass
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, val):
        self._value = int(val)


class MockMCP23017:
    """Mock MCP23017 16-bit I/O Expander."""
    
    def __init__(self, i2c, address=0x20):
        self.address = address
        self._pins = {i: MockMCP23017Pin(i) for i in range(16)}
        print(f"[MOCK] MCP23017 I/O Expander initialized at address {address}")
    
    def get_pin(self, pin_num):
        """Get a pin object."""
        return self._pins.get(pin_num, MockMCP23017Pin(pin_num))
    
    def set_pin(self, pin_num, value):
        """Set a pin value."""
        pin = self.get_pin(pin_num)
        pin.value = value


# ==================== Module Exports ====================
class MockBusio:
    """Mock busio module."""
    I2C = MockI2C


class MockAdafruitMCP4728:
    """Mock adafruit_mcp4728 module."""
    MCP4728 = MockMCP4728


class MockAdafruitADS1x15:
    """Mock adafruit_ads1x15.ads1115 module."""
    ADS1115 = MockADS1115
    P0 = P0
    P1 = P1
    P2 = P2
    P3 = P3


class MockAdafruitMCP230xx:
    """Mock adafruit_mcp230xx.mcp23017 module."""
    MCP23017 = MockMCP23017


class MockAnalogIn:
    """Mock adafruit_ads1x15.analog_in module."""
    _ADS1X15_DIFF_CHANNELS = _ADS1X15_DIFF_CHANNELS
    _ADS1X15_PGA_RANGE = _ADS1X15_PGA_RANGE


# ==================== Mock Blinka I2C ====================
class MockBlinka_I2C:
    """Mock Blinka I2C for Linux-style I2C."""
    MASTER = 1
    
    def __init__(self, bus_id, mode=1, baudrate=400000):
        self.bus_id = bus_id
        self.mode = mode
        self.baudrate = baudrate
        print(f"[MOCK] Blinka I2C initialized on bus {bus_id}")

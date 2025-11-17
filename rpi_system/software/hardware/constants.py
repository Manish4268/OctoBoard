"""Global constants used across the MPP tracker system."""

import numpy as np
import os

# ==================== SIMULATION MODE ====================
# Set to True for development without Raspberry Pi hardware
# Set to False when running on actual hardware
# This can be overridden via environment variable or command-line argument
SIMULATION_MODE = os.environ.get('OCTOBOARD_SIMULATION', 'False').lower() in ('true', '1', 'yes')
# =========================================================

# Board Manager Configuration
BOARD_DEFAULT_I2C_NUM = 1
BOARD_DEFAULT_OFFSET_RANGE = range(0, 12)  # 12 Octoboards = 96 channels
BOARD_DEFAULT_ITERATIONS = 10
BOARD_DEFAULT_INTERVAL = 0.001  # seconds

# System Configuration
TOTAL_BOARDS_PER_RPI = 12  # 12 Octoboards per Raspberry Pi
TOTAL_CHANNELS_PER_RPI = 96  # 12 × 8 = 96 channels
SAMPLES_PER_RPI = 24  # 96 channels ÷ 4 pixels = 24 samples
PIXELS_PER_SAMPLE = 4  # Each sample has 4 pixels: a, b, c, d

# I2C Device Base Addresses
I2C_BASE_MUX = 32    # Base address for MCP23017 multiplexer
I2C_BASE_ADC = 72    # Base address for ADS1115 ADC
I2C_BASE_DAC_0 = 96  # Base address for first MCP4728 DAC
I2C_BASE_DAC_1 = 97  # Base address for second MCP4728 DAC

# List of base addresses in order: MUX, ADC, DAC_0, DAC_1
I2C_BASE_ADDRESSES = [I2C_BASE_MUX, I2C_BASE_ADC, I2C_BASE_DAC_0, I2C_BASE_DAC_1]

# Address offset multipliers for different devices
I2C_OFFSET_MULTIPLIER = {
    I2C_BASE_MUX: 1,    # MUX uses 1x offset
    I2C_BASE_ADC: 1,    # ADC uses 1x offset
    I2C_BASE_DAC_0: 2,  # DACs use 2x offset
    I2C_BASE_DAC_1: 2   # DACs use 2x offset
}


# Softdac Configuration
SOFTDAC_MUX_PINS = [8, 9, 10, 11]  # Multiplexer pins used for gain control
SOFTDAC_DEFAULT_VREF = 5.0          # Default reference voltage (V)

# Gain Configurations
SOFTDAC_GAIN_VOLTAGES = np.array([
    0.04242424,  # Gain level 0
    0.09060606,  # Gain level 1
    0.13303030,  # Gain level 2
    0.19878788,  # Gain level 3
    0.24121212,  # Gain level 4
    0.28878788,  # Gain level 5
    0.33030303,  # Gain level 6
    0.42030303   # Gain level 7
])

# Pin state configurations for each gain level
# Format: [PIN_8, PIN_9, PIN_10, PIN_11]
SOFTDAC_GAIN_REGISTERS = np.array([
    [0, 0, 0, 0],  # Gain level 0
    [1, 0, 0, 0],  # Gain level 1
    [0, 1, 0, 0],  # Gain level 2
    [1, 1, 0, 0],  # Gain level 3
    [0, 0, 1, 0],  # Gain level 4
    [1, 0, 1, 0],  # Gain level 5
    [0, 1, 1, 0],  # Gain level 6
    [1, 1, 1, 0],  # Gain level 7
    [0, 0, 0, 1]   # Gain level 8
])

# General Board Configuration
CHANNELS_PER_BOARD = 8
MAX_CHANNELS_PER_DAC = 4
I2C_DAC_CHANNELS = ['channel_a', 'channel_b', 'channel_c', 'channel_d']

# Channel Configuration
CHANNEL_DEFAULT_SHUNT_RESISTANCE = 20     # Default shunt resistance (Ohms)
CHANNEL_VOLTAGE_LIMITS = (0, 1.2)         # Default voltage limits (V)
CHANNEL_INITIAL_VOLTAGE = 0.0             # Starting voltage for MPP tracking (V)
CHANNEL_INITIAL_DIRECTION = 1             # Initial direction for MPP tracking
CHANNEL_INITIAL_POWER = 0.0               # Initial power value
CHANNEL_INITIAL_VOLTAGE_STEP = 0.05       # Initial voltage step size (V)
CHANNEL_MAX_VOLTAGE_STEP = 0.2            # Maximum voltage step size (V)
CHANNEL_MIN_VOLTAGE_STEP = 2e-3           # Minimum voltage step size (V)

# ADC Configuration for Channel
CHANNEL_VOLTAGE_GAIN = 2                  # Default gain for voltage measurements
CHANNEL_CURRENT_GAIN = 16                 # Default gain for current measurements; Note: this eems to be used as data rate for some reason. (oboard.py)
# CHANNEL_CURRENT_GAIN = 2

CHANNEL_ADC_SETTLE_TIME = 0.01           # ADC settling time (seconds)

# MPP Tracking Parameters
CHANNEL_POWER_INCREASE_FACTOR = 1.1       # Factor to increase step size when power increases
CHANNEL_POWER_DECREASE_FACTOR = 0.3       # Factor to decrease step size when power decreases

# DAC Configuration
CHANNEL_DAC_GAIN = 1                      # Default DAC gain
# CHANNEL_DAC_VOLTAGE_SCALE = 2**16 / 8    # DAC voltage scaling factor (16-bit, 0-4V range)
CHANNEL_DAC_VOLTAGE_SCALE = 31.25e-6

# I/O Configuration
CHANNEL_DATA_DIRECTORY = "data"           # Directory for MPP tracking data
CHANNEL_IV_DIRECTORY = "IV"               # Directory for IV sweep data
CHANNEL_DEFAULT_HEADER = 'timestamp,measured_voltage,measured_current,dac_value,adc_gain_v,adc_gain_c'

# IV Sweep Configuration
CHANNEL_IV_START_VALUE = 0.0               # Default start value for IV sweep (V)
CHANNEL_IV_END_VALUE = 1.2                 # Default end value for IV sweep (V)
CHANNEL_IV_STEP_SIZE = 0.01                # Default step size for IV sweep (V)

# IV Sweep Scheduling (DEPRECATED - now controlled per-sample from Main PC)
IV_SWEEP_INTERVAL_HOURS = 1                # DEFAULT: 1 hour (60 minutes)
IV_SWEEP_INTERVAL_SECONDS = 3600           # DEFAULT: 1 hour = 3600 seconds
# NOTE: Actual interval is set by Main PC via sweep_interval_minutes parameter (1-1000 min)

# File Transfer Configuration
# IMPORTANT: Change MAIN_PC_IP for production deployment!
# - Development (Windows): "localhost"
# - Production (Raspberry Pi): "192.168.1.100" (your Main PC's actual IP)
import os
MAIN_PC_IP = os.environ.get('MAIN_PC_IP', 'localhost')  # Can override via environment variable
MAIN_PC_PORT = 8000                        # Main PC file receiver port
FILE_TRANSFER_TIMEOUT = 30                 # File transfer timeout (seconds)
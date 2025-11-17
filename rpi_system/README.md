# Raspberry Pi System

This code runs on each Raspberry Pi to control 96 channels (12 Octoboards).

## Hardware Configuration

- **12 Octoboards** per Raspberry Pi
- **96 channels** total (12 × 8)
- **24 samples** capacity (each sample uses 4 channels for 4 pixels)
- **I2C Bus:** Typically bus 1
- **I2C Address Offsets:** 0-11 (for 12 boards)

## Features

- Controls 96 channels via 12 Octoboards
- Handles 24 samples simultaneously (4 pixels each)
- Hourly IV sweep generation (every 1 hour)
- Automatic file transfer to Main PC via LAN
- REST API for remote control from Main PC
- Simulation mode for testing without hardware

## Installation

```bash
cd rpi_system/
pip install -r requirements.txt
```

## Configuration

Set environment variables:

```bash
export RPI_ID=rpi_1              # or rpi_2, rpi_3
export OCTOBOARD_I2C_BUS=1       # I2C bus number
export MAIN_PC_IP=192.168.1.100  # Main PC IP address
export API_PORT=8001              # API server port
```

## Running

### Production Mode (on Raspberry Pi):

```bash
python api_server.py
```

### Simulation Mode (for testing on Windows/Mac):

```bash
export OCTOBOARD_SIMULATION=True
python api_server.py
```

## API Endpoints

### Status and Info

- `GET /` - API information
- `GET /status` - RPi status
- `GET /channels` - List all 96 channels (24 sample slots)

### Measurements

- `POST /measurement/start` - Start measuring a sample
- `POST /measurement/stop/{sample_id}` - Stop measuring a sample
- `GET /measurement/{sample_id}` - Get sample measurement status

## Sample Configuration

Each sample occupies 4 consecutive channels for 4 pixels (a, b, c, d):

```json
{
  "sample_id": "Sample_001",
  "start_channel": 0,
  "cell_area": 0.09,
  "current_limit": 50,
  "start_voltage": 0.0,
  "stop_voltage": 1.2,
  "voltage_step": 0.01,
  "settle_time": 0.1,
  "measurement_type": "iv_sweep"
}
```

### Channel Allocation:

- Sample 1: channels 0-3 (pixels a, b, c, d)
- Sample 2: channels 4-7 (pixels a, b, c, d)
- ...
- Sample 24: channels 92-95 (pixels a, b, c, d)

## Hourly IV Sweeps

- Configured in `software/hardware/constants.py`: `IV_SWEEP_INTERVAL_HOURS = 1`
- Runs IV sweep for all active samples every hour
- Generates timestamped files: `IV_2025-11-17_10-00-00.csv`
- Automatically transfers files to Main PC

## File Transfer

Files are sent to Main PC via HTTP POST:
- **URL:** `http://{MAIN_PC_IP}:8000/upload`
- **Method:** POST with multipart/form-data
- **Timeout:** 30 seconds (configurable)

## Directory Structure

```
rpi_system/
├── api_server.py              # Main API server
├── software/                  # Hardware control code
│   ├── __init__.py
│   ├── cli.py
│   ├── logger.py
│   └── hardware/
│       ├── channel.py         # Single channel control
│       ├── oboard.py          # Single board (8 channels)
│       ├── manager.py         # Multi-board manager
│       ├── constants.py       # Configuration
│       ├── i2c.py             # I2C interface
│       ├── sdac.py            # Software DAC
│       └── mock_hardware.py   # Simulation mode
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## Troubleshooting

### RPi can't detect all 12 boards:
```bash
# Check I2C devices
i2cdetect -y 1
```

### Main PC connection fails:
- Verify Main PC file receiver is running
- Check network connectivity: `ping 192.168.1.100`
- Check firewall settings

### Simulation mode not working:
```bash
# Make sure simulation flag is set
echo $OCTOBOARD_SIMULATION
export OCTOBOARD_SIMULATION=True
```

## Network Requirements

- **LAN/Ethernet connection** (no internet required)
- **Static IP recommended:** 192.168.1.101-103
- **Open Ports:**
  - 8001: RPi API server
  - 8000: Main PC file receiver (outgoing)

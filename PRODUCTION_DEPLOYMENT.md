# OctoBoard Production Deployment Guide

## 🚀 Deploying to Real Raspberry Pi

### Prerequisites on Raspberry Pi
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+
sudo apt install python3 python3-pip python3-venv -y

# Enable I2C
sudo raspi-config
# → Interface Options → I2C → Enable

# Verify I2C is enabled
ls /dev/i2c-*
# Should show: /dev/i2c-1

# Install I2C tools to scan devices
sudo apt install i2c-tools -y

# Scan I2C bus (run this AFTER connecting Octoboards)
sudo i2cdetect -y 1
```

### Step 1: Transfer Code to Raspberry Pi

**Option A: Using Git (Recommended)**
```bash
# On Raspberry Pi
cd /home/pi
git clone https://github.com/Manish4268/OctoBoard.git
cd OctoBoard/rpi_system
```

**Option B: Using SCP from Windows**
```powershell
# On Windows (from OctoBoard folder)
scp -r rpi_system pi@<RPI_IP_ADDRESS>:/home/pi/
```

### Step 2: Setup Virtual Environment on RPi

```bash
# On Raspberry Pi
cd /home/pi/OctoBoard/rpi_system

# Create virtual environment
python3 -m venv venv

# Activate venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install I2C libraries
pip install adafruit-circuitpython-busdevice
pip install adafruit-circuitpython-mcp4728
pip install adafruit-circuitpython-ads1x15
pip install adafruit-circuitpython-mcp230xx
```

### Step 3: Configure for Production

**Edit `software/hardware/constants.py`:**
```python
# Change from localhost to actual Main PC IP
MAIN_PC_IP = "192.168.1.100"  # Your Main PC's IP address
MAIN_PC_PORT = 8000
```

**Set environment variables:**
```bash
# On Raspberry Pi
export RPI_ID="rpi_1"           # or rpi_2, rpi_3
export OCTOBOARD_SIMULATION="False"  # IMPORTANT: Turn off simulation!
export OCTOBOARD_I2C_BUS="1"    # Default I2C bus
export API_PORT="8001"          # 8001 for RPi1, 8002 for RPi2, 8003 for RPi3
```

### Step 4: Test Hardware Detection

```bash
# Activate venv
source venv/bin/activate

# Run test to detect boards
python -c "
from software import get_hardware_classes
OBoardManager, _, _, _ = get_hardware_classes()
manager = OBoardManager(i2c_num=1)
print(f'Detected {len(manager.oboards)} Octoboards')
print(f'Total channels: {len(manager.oboards) * 8}')
"
```

**Expected output:**
```
Found I2C devices at addresses: {32, 72, 96, 97, ...}
Successfully initialized OBoard with I2C offset 0
Detected 1 Octoboards
Total channels: 8
```

### Step 5: Test API Server

```bash
# Start server
export RPI_ID="rpi_1"
export OCTOBOARD_SIMULATION="False"
export API_PORT="8001"
python api_server.py
```

**Expected output:**
```
[rpi_1] Starting up...
[rpi_1] Simulation Mode: False
[rpi_1] Total Channels: 96
[rpi_1] Sample Capacity: 24
Found I2C devices at addresses: {32, 72, 96, 97}
Successfully initialized OBoard with I2C offset 0
[rpi_1] Initialized 1 boards
[rpi_1] Scheduler started (per-sample intervals)
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### Step 6: Configure Main PC

**Edit `main_pc_system/dashboard.py`:**
```python
# Change RPi URLs from localhost to actual IPs
RPIS = {
    "RPi 1": {"url": "http://192.168.1.101:8001", "id": "rpi_1"},
    "RPi 2": {"url": "http://192.168.1.102:8002", "id": "rpi_2"},
    "RPi 3": {"url": "http://192.168.1.103:8003", "id": "rpi_3"},
}
```

### Step 7: Create Systemd Service (Auto-start on boot)

**Create service file:**
```bash
sudo nano /etc/systemd/system/octoboard.service
```

**Service content:**
```ini
[Unit]
Description=OctoBoard RPi API Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/OctoBoard/rpi_system
Environment="RPI_ID=rpi_1"
Environment="OCTOBOARD_SIMULATION=False"
Environment="OCTOBOARD_I2C_BUS=1"
Environment="API_PORT=8001"
ExecStart=/home/pi/OctoBoard/rpi_system/venv/bin/python api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start service:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable octoboard

# Start service now
sudo systemctl start octoboard

# Check status
sudo systemctl status octoboard

# View logs
sudo journalctl -u octoboard -f
```

### Step 8: Network Configuration

**On Main PC (Windows):**
1. Open Firewall settings
2. Allow inbound connections on port 8000
3. Note your PC's IP address: `ipconfig` → IPv4 Address

**On Raspberry Pi:**
```bash
# Check if RPi can reach Main PC
ping 192.168.1.100

# Test file receiver
curl http://192.168.1.100:8000/ping
```

### Step 9: Verify Everything Works

**Checklist:**
- [ ] I2C enabled on RPi: `ls /dev/i2c-*`
- [ ] Octoboards detected: `sudo i2cdetect -y 1`
- [ ] API server running: `curl http://localhost:8001/status`
- [ ] Main PC reachable from RPi: `ping 192.168.1.100`
- [ ] File receiver running on Main PC
- [ ] Dashboard can connect to RPi
- [ ] Sample measurement creates files
- [ ] Files transferred to Main PC

## 🔧 Troubleshooting

### Issue: No I2C devices detected
```bash
# Check I2C is enabled
sudo raspi-config

# Check I2C modules loaded
lsmod | grep i2c

# Manual load
sudo modprobe i2c-dev
```

### Issue: Permission denied on I2C
```bash
# Add user to i2c group
sudo usermod -a -G i2c pi
sudo reboot
```

### Issue: Import errors
```bash
# Reinstall in venv
source venv/bin/activate
pip install --force-reinstall -r requirements.txt
```

### Issue: Cannot connect to Main PC
```bash
# Check firewall on Windows
# Check IP address is correct
# Test with: curl http://<MAIN_PC_IP>:8000/ping
```

## 📊 Scaling to Multiple RPis

**For RPi 2:**
- Set `RPI_ID=rpi_2`
- Set `API_PORT=8002`
- Use different IP: `192.168.1.102`

**For RPi 3:**
- Set `RPI_ID=rpi_3`
- Set `API_PORT=8003`
- Use different IP: `192.168.1.103`

## 🎯 Testing Production Setup

**Test 1: Hardware Detection**
- Expected: Automatically detects 1-12 Octoboards
- System adapts to available channels

**Test 2: IV Sweep**
- Start measurement from dashboard
- Verify files appear on Main PC
- Check Config.txt and Status files

**Test 3: Auto-recovery**
- Unplug network cable → Replug
- Should reconnect automatically
- Files should resume transferring

**Test 4: Scaling**
- Add more Octoboards
- Restart API server
- Should detect new boards automatically

## ✅ System is Production-Ready When:
1. API server starts on RPi boot
2. Boards detected automatically (any number 1-12)
3. Files transfer to Main PC successfully
4. Dashboard shows correct channel count
5. System recovers from network issues
6. Status files persist across restarts

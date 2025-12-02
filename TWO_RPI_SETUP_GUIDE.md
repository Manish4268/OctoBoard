================================================================================
                    TWO RASPBERRY PI SETUP GUIDE
                    Complete Step-by-Step Instructions
================================================================================

HARDWARE YOU HAVE:
- 2× Raspberry Pi (192.168.2.10 and 192.168.2.11)
- 1× TP-Link 5-Port Gigabit Switch
- 3× Ethernet cables
- 1× Windows PC
- Octoboards (to be connected to RPis)
- PuTTY and WinSCP installed on Windows

================================================================================
PART 1: PHYSICAL CONNECTIONS
================================================================================

Step 1: Connect Everything
---------------------------

1. Plug TP-Link Switch into power outlet

2. Connect Ethernet cables:
   - Cable 1: Windows PC → Switch (any port)
             (Use USB-to-Ethernet adapter if PC has no Ethernet port)
   - Cable 2: RPi 1 → Switch (any port)
   - Cable 3: RPi 2 → Switch (any port)

3. Power on both Raspberry Pis

4. Wait 1 minute for RPis to boot


================================================================================
PART 2: WINDOWS PC NETWORK CONFIGURATION
================================================================================

Step 2: Set Static IP on Windows
---------------------------------

1. Press Windows Key + R
2. Type: ncpa.cpl
3. Press Enter

4. Find your Ethernet adapter (might be called "Ethernet" or "Local Area Connection")
   - If using USB-to-Ethernet, look for new adapter that appeared

5. Right-click the adapter → Properties

6. Double-click "Internet Protocol Version 4 (TCP/IPv4)"

7. Select "Use the following IP address"
   - IP address: 192.168.2.1
   - Subnet mask: 255.255.255.0
   - Default gateway: (leave blank)
   - DNS servers: (leave blank)

8. Click OK → OK

9. Close Network Connections window

Step 3: Verify Windows IP
--------------------------

Open PowerShell and run:
```powershell
ipconfig
```

You should see:
```
Ethernet adapter Ethernet:
   IPv4 Address: 192.168.2.1
   Subnet Mask: 255.255.255.0
```


================================================================================
PART 3: RASPBERRY PI 1 SETUP (192.168.2.10)
================================================================================

Step 4: Connect to RPi 1 via PuTTY
-----------------------------------

1. Open PuTTY

2. Enter:
   - Host Name: 192.168.2.10
   - Port: 22
   - Connection type: SSH

3. Click "Open"

4. Login:
   - Username: pi
   - Password: raspberry (or your password)

Step 5: Transfer Files to RPi 1 via WinSCP
-------------------------------------------

1. Open WinSCP

2. New Session:
   - File protocol: SFTP
   - Host name: 192.168.2.10
   - Port number: 22
   - User name: pi
   - Password: raspberry (or your password)

3. Click "Login"

4. In WinSCP:
   - Left panel (Windows): Navigate to C:\Users\ManishJadhav\OctoBoard\rpi_system
   - Right panel (RPi): Navigate to /home/pi/
   
5. Drag the entire "rpi_system" folder from left to right

6. Wait for transfer to complete (may take 2-5 minutes)

7. Keep WinSCP open for later

Step 6: Configure RPi 1 (in PuTTY)
-----------------------------------

Run these commands one by one:

```bash
# Navigate to project
cd ~/rpi_system

# Verify start_rpi.sh configuration
cat start_rpi.sh | grep "export RPI_ID"
cat start_rpi.sh | grep "export MAIN_PC_IP"
cat start_rpi.sh | grep "export API_PORT"
```

You should see:
```
export RPI_ID="${RPI_ID:-rpi_1}"
export MAIN_PC_IP="${MAIN_PC_IP:-192.168.2.1}"
export API_PORT="${API_PORT:-8001}"
```

If correct, continue:

```bash
# Make start script executable
chmod +x start_rpi.sh

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your prompt now

# Install Python packages (this takes 10-15 minutes)
pip install numpy>=1.22 fastapi>=0.104.0 uvicorn>=0.24.0 pydantic>=2.0.0 requests>=2.31.0 schedule>=1.2.0 adafruit-blinka>=7.3.3 adafruit-circuitpython-mcp4728>=1.0.8 adafruit-circuitpython-ads1x15>=2.3.9 adafruit-circuitpython-mcp230xx>=1.0.10
```

Wait for installation to complete...

```bash
# Enable I2C interface
sudo raspi-config
```

In raspi-config menu:
- Use arrow keys to navigate
- Select: "3 Interface Options"
- Select: "I5 I2C"
- Select: "Yes" to enable
- Select: "Ok"
- Select: "Finish"
- Select: "Yes" to reboot

RPi 1 will reboot now. Wait 1 minute.

Step 7: Transfer Updated Files to RPi 1 (Important!)
-----------------------------------------------------

Since you edited channel.py on Windows, transfer updated files:

1. In WinSCP (reconnect to 192.168.2.10 if needed)
2. Navigate to: C:\Users\ManishJadhav\OctoBoard\rpi_system\software\hardware\
3. Transfer these files to /home/pi/rpi_system/software/hardware/:
   - channel.py (the fixed version)
   - Any other files you modified

Step 8: Test RPi 1 Server
--------------------------

1. Reconnect PuTTY to 192.168.2.10

2. Login and run:

```bash
cd ~/rpi_system
source venv/bin/activate
./start_rpi.sh
```

Expected output:
```
🚀 Starting OctoBoard RPi API Server
=========================================
RPi ID: rpi_1
Main PC IP: 192.168.2.1
API Port: 8001
Simulation Mode: False
I2C Bus: 1
=========================================
✅ I2C enabled
📡 Scanning I2C devices...
(shows I2C scan - should show Octoboard addresses if connected)
✅ Main PC reachable
🚀 Starting API server...
Successfully initialized OBoard with I2C offset 0
Successfully initialized OBoard with I2C offset 1
Successfully initialized OBoard with I2C offset 2
INFO: Uvicorn running on http://0.0.0.0:8001
```

✅ RPi 1 is now running! Keep this PuTTY window open.


================================================================================
PART 4: RASPBERRY PI 2 SETUP (192.168.2.11)
================================================================================

Step 9: Connect to RPi 2 via PuTTY
-----------------------------------

1. Open NEW PuTTY window (don't close RPi 1 window)

2. Enter:
   - Host Name: 192.168.2.11
   - Port: 22
   - Connection type: SSH

3. Click "Open"

4. Login:
   - Username: pi
   - Password: raspberry (or your password)

Step 10: Transfer Files to RPi 2 via WinSCP
--------------------------------------------

1. Open NEW WinSCP session (or disconnect current and reconnect)

2. New Session:
   - File protocol: SFTP
   - Host name: 192.168.2.11
   - Port number: 22
   - User name: pi
   - Password: raspberry (or your password)

3. Click "Login"

4. In WinSCP:
   - Left panel (Windows): Navigate to C:\Users\ManishJadhav\OctoBoard\rpi_system
   - Right panel (RPi): Navigate to /home/pi/
   
5. Drag the entire "rpi_system" folder from left to right

6. Wait for transfer to complete (may take 2-5 minutes)

Step 11: Configure RPi 2 (in PuTTY)
------------------------------------

⚠️ IMPORTANT: RPi 2 needs DIFFERENT configuration!

Run these commands:

```bash
# Navigate to project
cd ~/rpi_system

# Edit the start script for RPi 2
nano start_rpi.sh
```

In nano editor:
1. Use arrow keys to navigate to line 6
2. Change:   export RPI_ID="${RPI_ID:-rpi_1}"
   To:       export RPI_ID="${RPI_ID:-rpi_2}"

3. Navigate to line 8
4. Change:   export API_PORT="${API_PORT:-8001}"
   To:       export API_PORT="${API_PORT:-8002}"

5. Line 7 should already be: export MAIN_PC_IP="${MAIN_PC_IP:-192.168.2.1}"

6. Save and exit:
   - Press Ctrl+O (save)
   - Press Enter (confirm)
   - Press Ctrl+X (exit)

Verify the changes:
```bash
cat start_rpi.sh | grep "export RPI_ID"
cat start_rpi.sh | grep "export MAIN_PC_IP"
cat start_rpi.sh | grep "export API_PORT"
```

Should show:
```
export RPI_ID="${RPI_ID:-rpi_2}"
export MAIN_PC_IP="${MAIN_PC_IP:-192.168.2.1}"
export API_PORT="${API_PORT:-8002}"
```

Continue setup:

```bash
# Make start script executable
chmod +x start_rpi.sh

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python packages (this takes 10-15 minutes)
pip install numpy>=1.22 fastapi>=0.104.0 uvicorn>=0.24.0 pydantic>=2.0.0 requests>=2.31.0 schedule>=1.2.0 adafruit-blinka>=7.3.3 adafruit-circuitpython-mcp4728>=1.0.8 adafruit-circuitpython-ads1x15>=2.3.9 adafruit-circuitpython-mcp230xx>=1.0.10
```

Wait for installation to complete...

```bash
# Enable I2C interface
sudo raspi-config
```

In raspi-config menu:
- Select: "3 Interface Options"
- Select: "I5 I2C"
- Select: "Yes" to enable
- Select: "Ok"
- Select: "Finish"
- Select: "Yes" to reboot

RPi 2 will reboot now. Wait 1 minute.

Step 12: Test RPi 2 Server
---------------------------

1. Reconnect PuTTY to 192.168.2.11

2. Login and run:

```bash
cd ~/rpi_system
source venv/bin/activate
./start_rpi.sh
```

Expected output:
```
🚀 Starting OctoBoard RPi API Server
=========================================
RPi ID: rpi_2
Main PC IP: 192.168.2.1
API Port: 8002
Simulation Mode: False
I2C Bus: 1
=========================================
✅ I2C enabled
📡 Scanning I2C devices...
(shows I2C scan)
✅ Main PC reachable
🚀 Starting API server...
Successfully initialized OBoard...
INFO: Uvicorn running on http://0.0.0.0:8002
```

✅ RPi 2 is now running! Keep this PuTTY window open.


================================================================================
PART 5: WINDOWS DASHBOARD CONFIGURATION
================================================================================

Step 13: Update Dashboard for 2 RPis
-------------------------------------

1. On Windows, open file:
   C:\Users\ManishJadhav\OctoBoard\main_pc_system\dashboard.py

2. Find line ~21 (look for RPIS = {)

3. Change from:
```python
RPIS = {
    "RPi 1": {"url": "http://192.168.2.10:8001", "id": "rpi_1"},
    # "RPi 2": {"url": "http://192.168.2.11:8002", "id": "rpi_2"},
    # "RPi 3": {"url": "http://192.168.2.12:8003", "id": "rpi_3"},
}
```

To:
```python
RPIS = {
    "RPi 1": {"url": "http://192.168.2.10:8001", "id": "rpi_1"},
    "RPi 2": {"url": "http://192.168.2.11:8002", "id": "rpi_2"},
    # "RPi 3": {"url": "http://192.168.2.12:8003", "id": "rpi_3"},  # Add when available
}
```

4. Save the file (Ctrl+S)


================================================================================
PART 6: START WINDOWS DASHBOARD AND FILE RECEIVER
================================================================================

Step 14: Start File Receiver
-----------------------------

1. Open PowerShell (Terminal 1)

2. Run:
```powershell
cd C:\Users\ManishJadhav\OctoBoard\main_pc_system
.\venv\Scripts\Activate.ps1
python file_receiver.py
```

Expected output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ File receiver is running! Keep this window open.

Step 15: Start Dashboard
-------------------------

1. Open NEW PowerShell (Terminal 2)

2. Run:
```powershell
cd C:\Users\ManishJadhav\OctoBoard\main_pc_system
.\venv\Scripts\Activate.ps1
streamlit run dashboard.py
```

Expected output:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.2.1:8501
```

3. Browser should open automatically to http://localhost:8501

✅ Dashboard is running!


================================================================================
PART 7: VERIFY EVERYTHING IS WORKING
================================================================================

Step 16: Check Dashboard
-------------------------

In the browser at http://localhost:8501:

1. Look at left sidebar under "Raspberry Pis"
   Should show:
   ✅ RPi 1 (with channel count)
   ✅ RPi 2 (with channel count)

2. Both should show green checkmarks and "Online" status

3. Check "System Overview" tab
   - Should show both RPis online
   - Total available channels
   - System capacity

Step 17: Test Ping from Windows
--------------------------------

Open PowerShell and test:
```powershell
ping 192.168.2.10
ping 192.168.2.11
```

Both should reply successfully!


================================================================================
PART 8: RUNNING MEASUREMENTS (WHEN READY)
================================================================================

Step 18: Connect Octoboards
----------------------------

1. Connect Octoboards to each Raspberry Pi via I2C
2. Restart each RPi server (in PuTTY):
   - Press Ctrl+C to stop
   - Run: ./start_rpi.sh
3. Check I2C scan output shows Octoboard addresses

Step 19: Start Your First Measurement
--------------------------------------

1. In Dashboard, go to "New Measurement" tab

2. Fill in:
   - Sample ID: TEST_001
   - Cell Area: 0.09 cm²
   - Current Limit: 50 mA
   - Start Voltage: 0 V
   - Stop Voltage: 1.2 V
   - Voltage Step: 0.01 V
   - Settle Time: 0.1 s
   - Sweep Interval: 60 minutes

3. Select Raspberry Pi (RPi 1 or RPi 2)
   - Channels will auto-assign

4. Click "🚀 Start Measurement"

5. Go to "Active Measurements" tab to monitor

6. Files will be saved to:
   C:\Users\ManishJadhav\SynologyDrive\Rayleigh\Outdoor Data\TEST_001\


================================================================================
TROUBLESHOOTING
================================================================================

Problem: Can't connect to RPi via PuTTY
----------------------------------------
Solution:
1. Check Ethernet cables are plugged in
2. Check switch has power
3. Verify Windows IP is 192.168.2.1 (run: ipconfig)
4. Try ping: ping 192.168.2.10

Problem: Dashboard shows RPis offline
--------------------------------------
Solution:
1. Check both RPi servers are running (PuTTY windows)
2. Verify dashboard.py has correct IPs and ports
3. Restart dashboard (Ctrl+C and run again)

Problem: File receiver not receiving files
-------------------------------------------
Solution:
1. Check file receiver is running on port 8000
2. Verify folder exists: C:\Users\ManishJadhav\SynologyDrive\Rayleigh\Outdoor Data
3. Check RPis can reach PC: ping 192.168.2.1 (from PuTTY)

Problem: I2C devices not detected
----------------------------------
Solution:
1. Check Octoboard power supply
2. Check I2C cables connected properly
3. Verify I2C enabled: sudo raspi-config
4. Reboot RPi: sudo reboot


================================================================================
NETWORK CONFIGURATION SUMMARY
================================================================================

Device          IP Address       Port    Purpose
-----------     --------------   -----   ---------------------------------
Windows PC      192.168.2.1      8000    File Receiver
Windows PC      192.168.2.1      8501    Dashboard (localhost)
RPi 1           192.168.2.10     8001    API Server (rpi_1)
RPi 2           192.168.2.11     8002    API Server (rpi_2)
Switch          N/A              N/A     Connects all devices


================================================================================
QUICK REFERENCE COMMANDS
================================================================================

On RPi (PuTTY):
---------------
cd ~/rpi_system
source venv/bin/activate
./start_rpi.sh                    # Start server
Ctrl+C                            # Stop server
nano start_rpi.sh                 # Edit configuration
sudo i2cdetect -y 1               # Scan I2C devices
sudo reboot                       # Reboot RPi

On Windows (PowerShell):
------------------------
cd C:\Users\ManishJadhav\OctoBoard\main_pc_system
.\venv\Scripts\Activate.ps1
python file_receiver.py           # Start file receiver
streamlit run dashboard.py        # Start dashboard
ping 192.168.2.10                # Test RPi 1 connection
ping 192.168.2.11                # Test RPi 2 connection
ipconfig                         # Check PC IP address


================================================================================
DAILY STARTUP ROUTINE
================================================================================

1. Power on both Raspberry Pis (wait 1 minute)

2. Start RPi 1 server:
   - PuTTY → 192.168.2.10
   - cd ~/rpi_system
   - source venv/bin/activate
   - ./start_rpi.sh

3. Start RPi 2 server:
   - PuTTY → 192.168.2.11
   - cd ~/rpi_system
   - source venv/bin/activate
   - ./start_rpi.sh

4. Start File Receiver (PowerShell):
   - cd C:\Users\ManishJadhav\OctoBoard\main_pc_system
   - .\venv\Scripts\Activate.ps1
   - python file_receiver.py

5. Start Dashboard (PowerShell):
   - cd C:\Users\ManishJadhav\OctoBoard\main_pc_system
   - .\venv\Scripts\Activate.ps1
   - streamlit run dashboard.py

6. Open browser: http://localhost:8501

7. Start measurements! 🚀


================================================================================
END OF SETUP GUIDE
================================================================================

Questions? Check the troubleshooting section or review specific steps above.

Your system is now ready to run outdoor solar cell testing with 2 Raspberry Pis!

Total Capacity:
- 2 RPis × 96 channels = 192 channels
- 48 samples max (4 pixels each)
- Automated IV sweeps every 1-1000 minutes
- Data auto-transferred to Windows PC

Good luck with your experiments! 🌞⚡

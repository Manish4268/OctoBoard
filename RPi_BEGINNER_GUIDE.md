# 🎓 Complete Beginner's Guide to Raspberry Pi with OctoBoard

## 📋 Your Current Setup
- **Raspberry Pi** connected via **Ethernet cable** to your **Laptop**
- **1 Octoboard** connected to RPi's I2C pins
- **Laptop** running Windows with the dashboard

---

## 🔌 Step 1: Find Your Raspberry Pi's IP Address

### Option A: Using Your Router (Easiest)
1. Open your web browser
2. Go to your router's admin page (usually `192.168.1.1` or `192.168.0.1`)
3. Login (check router sticker for password)
4. Look for "Connected Devices" or "DHCP Clients"
5. Find device named "raspberrypi" - note its IP address (e.g., `192.168.1.150`)

### Option B: Using Windows Command Prompt
```powershell
# Open PowerShell and scan your network
arp -a

# Look for an entry like:
# 192.168.1.150    b8-27-eb-xx-xx-xx    dynamic
# The IP starting with b8-27-eb is likely your RPi
```

### Option C: Connect Monitor to RPi
1. Connect HDMI monitor and keyboard to RPi
2. Login (default: username=`pi`, password=`raspberry`)
3. Run command:
```bash
hostname -I
```
4. You'll see the IP address (e.g., `192.168.1.150`)

**Write down this IP address! Let's call it `<RPI_IP>`**

---

## 🔐 Step 2: Connect to Raspberry Pi via SSH

### What is SSH?
SSH lets you control your Raspberry Pi from your laptop's command line (no monitor needed!)

### Enable SSH on RPi (if not already enabled)
**If you have a monitor connected:**
```bash
sudo raspi-config
# Navigate to: Interface Options → SSH → Enable
```

**If you can't access RPi yet:**
- Take out the SD card
- Insert into your laptop
- Create an empty file named `ssh` (no extension) in the boot partition
- Put SD card back in RPi and boot

### Connect from Windows
1. **Open PowerShell** on your laptop
2. Type:
```powershell
ssh pi@<RPI_IP>
# Example: ssh pi@192.168.1.150
```

3. If asked "Are you sure?", type `yes`
4. **Default password:** `raspberry`

**✅ Success!** You should now see:
```
pi@raspberrypi:~ $
```

---

## 🌐 Step 3: Configure Network

### Check if RPi can access internet
```bash
ping google.com -c 4
# Press Ctrl+C to stop

# If it works, you'll see responses
# If not, your RPi needs internet access
```

### If RPi has no internet (direct laptop connection):
**Option 1: Share your laptop's WiFi with RPi**
1. On Windows: Settings → Network & Internet → Mobile hotspot → ON
2. Or connect RPi to same WiFi as laptop

**Option 2: Bridge connection (Advanced)**
- Share laptop's WiFi through Ethernet to RPi
- Not recommended for beginners

---

## 🛠️ Step 4: Setup Raspberry Pi

### Update System
```bash
# This takes 5-10 minutes
sudo apt update
sudo apt upgrade -y
```

### Install Python and Tools
```bash
# Install Python 3 and pip
sudo apt install python3 python3-pip python3-venv -y

# Install I2C tools
sudo apt install i2c-tools -y

# Install git (to download code)
sudo apt install git -y
```

### Enable I2C (for Octoboard communication)
```bash
sudo raspi-config
```

**Navigation:**
1. Use arrow keys to select: **3 Interface Options**
2. Press Enter
3. Select: **I5 I2C**
4. Select: **Yes**
5. Press Tab key to select **Finish**
6. **Reboot:** `sudo reboot`

**Wait 30 seconds**, then reconnect:
```powershell
ssh pi@<RPI_IP>
```

### Verify I2C is Enabled
```bash
ls /dev/i2c-*
# Should show: /dev/i2c-1
```

---

## 🔍 Step 5: Detect Your Octoboard

### Check I2C Devices
```bash
sudo i2cdetect -y 1
```

**What you should see:**
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10:          -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: 20 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30:          -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40:          -- -- -- -- -- -- -- -- 48 -- -- -- -- -- -- --
50:          -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: 60 61 -- -- -- -- -- -- -- -- -- -- -- -- -- --
70:          -- -- -- -- -- -- -- --
```

**Device addresses explained:**
- `20` = MCP23017 (I/O Expander) ✅
- `48` = ADS1115 (ADC) ✅
- `60`, `61` = MCP4728 (DAC) ✅

**If you see these addresses, your Octoboard is connected correctly!** 🎉

**If you see nothing or different addresses:**
- Check Octoboard is powered
- Check I2C wires (SDA, SCL, GND, 3.3V)
- Octoboard may have different I2C address offsets

---

## 📥 Step 6: Transfer OctoBoard Code to RPi

### Option A: Using Git (Recommended)
```bash
# Go to home directory
cd /home/pi

# Clone the repository
git clone https://github.com/Manish4268/OctoBoard.git

# Go into the rpi_system folder
cd OctoBoard/rpi_system
```

### Option B: Copy from Your Laptop
**On Windows PowerShell:**
```powershell
# Go to your OctoBoard folder
cd C:\Users\ManishJadhav\OctoBoard

# Copy rpi_system folder to RPi
scp -r rpi_system pi@<RPI_IP>:/home/pi/
```

**Then on RPi:**
```bash
cd /home/pi/rpi_system
```

---

## 🐍 Step 7: Setup Python Environment

```bash
# Make sure you're in rpi_system folder
cd /home/pi/rpi_system  # or /home/pi/OctoBoard/rpi_system

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
# You should see (venv) before your prompt

# Upgrade pip
pip install --upgrade pip

# Install dependencies (takes 5-10 minutes)
pip install -r requirements.txt

# Install Adafruit libraries for I2C
pip install adafruit-circuitpython-busdevice
pip install adafruit-circuitpython-mcp4728
pip install adafruit-circuitpython-ads1x15
pip install adafruit-circuitpython-mcp230xx
```

---

## 🧪 Step 8: Test Hardware Detection

```bash
# Make sure venv is activated
source venv/bin/activate

# Test if code can detect your Octoboard
python3 -c "
from software import get_hardware_classes
print('Trying to detect Octoboards...')
OBoardManager, _, _, _ = get_hardware_classes()
manager = OBoardManager(i2c_num=1)
print(f'✅ SUCCESS! Detected {len(manager.oboards)} Octoboard(s)')
print(f'Total channels: {len(manager.oboards) * 8}')
"
```

**Expected output:**
```
Trying to detect Octoboards...
Found I2C devices at addresses: {32, 72, 96, 97}
Successfully initialized OBoard with I2C offset 0
✅ SUCCESS! Detected 1 Octoboard(s)
Total channels: 8
```

**If you see errors:**
- Check I2C is enabled: `ls /dev/i2c-*`
- Check permissions: `sudo usermod -a -G i2c pi` then logout/login
- Check Octoboard connections

---

## ⚙️ Step 9: Configure for Your Network

### Edit Configuration File
```bash
nano software/hardware/constants.py
```

**Find this line (around line 119):**
```python
MAIN_PC_IP = os.environ.get('MAIN_PC_IP', 'localhost')
```

**Press Ctrl+X, then Y, then Enter to save**

### Set Environment Variables
```bash
# Edit startup script
nano start_rpi.sh
```

**Change these lines:**
```bash
export MAIN_PC_IP="192.168.1.100"  # Change to YOUR laptop's IP
export RPI_ID="rpi_1"
export API_PORT="8001"
export OCTOBOARD_SIMULATION="False"  # Important: False = real hardware
```

**Save:** Ctrl+X → Y → Enter

### Make Script Executable
```bash
chmod +x start_rpi.sh
```

---

## 🖥️ Step 10: Find Your Laptop's IP Address

**On Windows PowerShell:**
```powershell
ipconfig
```

**Look for:**
```
Ethernet adapter Ethernet:
   IPv4 Address. . . . . . . . : 192.168.1.100
```

**Or:**
```
Wireless LAN adapter Wi-Fi:
   IPv4 Address. . . . . . . . : 192.168.1.100
```

**This is your `MAIN_PC_IP`!** Write it down!

---

## 🚀 Step 11: Start the RPi Server

### On Raspberry Pi:
```bash
# Go to folder
cd /home/pi/rpi_system

# Activate venv
source venv/bin/activate

# Run the startup script
./start_rpi.sh
```

**You should see:**
```
🚀 Starting OctoBoard RPi API Server
=========================================
RPi ID: rpi_1
Main PC IP: 192.168.1.100
API Port: 8001
Simulation Mode: False
I2C Bus: 1
=========================================
🔍 Checking I2C...
✅ I2C enabled
📡 Scanning I2C devices...
[shows i2cdetect output]
🌐 Testing connection to Main PC...
✅ Main PC reachable
🚀 Starting API server...
[rpi_1] Starting up...
[rpi_1] Simulation Mode: False
Found I2C devices at addresses: {32, 72, 96, 97}
Successfully initialized OBoard with I2C offset 0
[rpi_1] Initialized 1 boards
INFO:     Uvicorn running on http://0.0.0.0:8001
```

**✅ If you see this, RPi is READY!**

---

## 💻 Step 12: Configure Main PC (Your Laptop)

### Update Dashboard Settings
**Open:** `C:\Users\ManishJadhav\OctoBoard\main_pc_system\dashboard.py`

**Find (around line 20) and change:**
```python
RPIS = {
    "RPi 1": {"url": "http://<RPI_IP>:8001", "id": "rpi_1"},  # Change <RPI_IP>!
    # "RPi 2": {"url": "http://192.168.1.102:8002", "id": "rpi_2"},  # Comment out
    # "RPi 3": {"url": "http://192.168.1.103:8003", "id": "rpi_3"},  # Comment out
}
```

**Example (if RPi IP is 192.168.1.150):**
```python
RPIS = {
    "RPi 1": {"url": "http://192.168.1.150:8001", "id": "rpi_1"},
}
```

**Save the file**

---

## 🎯 Step 13: Start Everything

### On Laptop (Windows PowerShell):

**Terminal 1 - File Receiver:**
```powershell
cd C:\Users\ManishJadhav\OctoBoard\main_pc_system
.\venv\Scripts\Activate.ps1
python file_receiver.py
```

**Terminal 2 - Dashboard:**
```powershell
cd C:\Users\ManishJadhav\OctoBoard\main_pc_system
.\venv\Scripts\Activate.ps1
streamlit run dashboard.py
```

**Terminal 3 - Keep RPi running via SSH**

---

## ✅ Step 14: Test Everything!

### Open Dashboard
1. Browser opens automatically to `http://localhost:8501`
2. **Check sidebar:** Should show "✅ RPi 1" (green)
3. **Check channels:** Should show "8" channels

### Run First Measurement
1. Go to **"New Measurement"** tab
2. Enter Sample ID: `Test_001`
3. Select **RPi 1**
4. Should show: **"Assigned Channels: 0-3"**
5. Click **"Start Measurement"**

### Check Files Arrive
1. Open: `C:\Users\ManishJadhav\SynologyDrive\Rayleigh\Outdoor Data`
2. You should see folder: `Test_001`
3. Inside: `a/`, `b/`, `c/`, `d/` folders with `.csv` files
4. Also: `Config.txt` and `rpi_1_Samples_Status.txt`

**If files appear: 🎉 SUCCESS! Everything works!**

---

## 🔧 Troubleshooting

### Problem: "Connection refused" in dashboard
**Solution:**
```bash
# On RPi, check if server is running:
ps aux | grep python

# If not running, start it:
cd /home/pi/rpi_system
source venv/bin/activate
./start_rpi.sh
```

### Problem: "Cannot reach Main PC"
**Solution:**
```powershell
# On Windows: Allow port 8000 in firewall
# Or temporarily disable firewall for testing
```

### Problem: No files appearing
**Check:**
1. RPi terminal shows "Transferred" messages?
2. File receiver terminal shows "[DEBUG] Receiving file"?
3. Check IP addresses are correct

### Problem: "Board not available" errors
**Solution:**
```bash
# Check I2C again:
sudo i2cdetect -y 1

# Restart RPi if needed:
sudo reboot
```

---

## 🎓 Understanding the System

### What happens when you start a measurement:

1. **Dashboard (Laptop)** → Sends config to **RPi API** via HTTP
2. **RPi API** → Saves config, schedules IV sweeps
3. **RPi Hardware** → Performs IV sweep on 4 channels (a,b,c,d)
4. **RPi** → Saves data to local `/tmp/` folder
5. **RPi** → Transfers files to **File Receiver (Laptop)** via HTTP POST
6. **File Receiver** → Saves files to SynologyDrive folder
7. **Dashboard** → Reads files and displays charts

### The 3 Running Programs:

1. **RPi API Server** (Port 8001) - Controls hardware, runs measurements
2. **File Receiver** (Port 8000) - Receives files from RPi
3. **Dashboard** (Port 8501) - Web interface for you to control everything

---

## 📝 Quick Reference Commands

### SSH into RPi:
```powershell
ssh pi@<RPI_IP>
```

### Start RPi Server:
```bash
cd /home/pi/rpi_system
source venv/bin/activate
./start_rpi.sh
```

### Check RPi Server Status:
```bash
ps aux | grep python
```

### Stop RPi Server:
```bash
# Press Ctrl+C in the terminal where it's running
```

### View RPi Logs:
```bash
# While server is running, logs appear in terminal
```

### Reboot RPi:
```bash
sudo reboot
```

---

## 🚀 Next Steps

Once everything works:

1. **Set up Auto-Start:** Follow `PRODUCTION_DEPLOYMENT.md` → Step 7 (systemd service)
2. **Add More RPis:** Repeat process with different RPI_ID and API_PORT
3. **Add More Octoboards:** Just connect them - system auto-detects!

---

## 📞 Getting Help

If stuck:
1. Check which step failed
2. Read error messages carefully
3. Check the troubleshooting section
4. Google specific error messages

**Common files to check:**
- RPi: `/home/pi/rpi_system/api_server.py`
- Laptop: `C:\Users\ManishJadhav\OctoBoard\main_pc_system\dashboard.py`
- Config: `C:\Users\ManishJadhav\OctoBoard\rpi_system\software\hardware\constants.py`

---

**You're ready to go! Follow each step carefully and you'll have it working! 🎉**

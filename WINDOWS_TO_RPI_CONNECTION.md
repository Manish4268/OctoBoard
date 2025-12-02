# 🔌 How to Connect to Raspberry Pi from Windows

## 📋 What You Need

### Hardware
- ✅ Raspberry Pi (any model with GPIO pins)
- ✅ Ethernet cable connecting RPi to your laptop/network
- ✅ Power supply for RPi (5V, 2.5A+)
- ✅ MicroSD card with Raspberry Pi OS installed
- ⚠️ Optional: HDMI monitor + keyboard (for initial setup)

### Software for Windows
We'll install these step by step below:
1. **PuTTY** - SSH client to connect to RPi
2. **WinSCP** - File transfer tool
3. **VS Code** (optional) - For editing code remotely
4. **IP Scanner** - To find your RPi

---

## 🎯 Step 1: Install Required Software

### Install PuTTY (SSH Client)

**What is PuTTY?**
PuTTY lets you control the Raspberry Pi using command line from your Windows PC.

**Download:**
1. Go to: https://www.putty.org/
2. Click: **Download PuTTY**
3. Download: `putty-64bit-0.xx-installer.msi`
4. Run the installer
5. Click **Next** → **Install** → **Finish**

**Where it is:** Start Menu → PuTTY → PuTTY

---

### Install WinSCP (File Transfer)

**What is WinSCP?**
WinSCP lets you drag-and-drop files between Windows and Raspberry Pi (like Windows Explorer).

**Download:**
1. Go to: https://winscp.net/eng/download.php
2. Download: **Installation package**
3. Run installer
4. Click **Next** → **Next** → **Install** → **Finish**

**Where it is:** Start Menu → WinSCP

---

### Install Advanced IP Scanner (Find RPi)

**What is Advanced IP Scanner?**
Scans your network to find all connected devices, including your Raspberry Pi.

**Download:**
1. Go to: https://www.advanced-ip-scanner.com/
2. Click **Download**
3. Run `advanced_ip_scanner.exe`
4. No installation needed - it runs directly!

---

### Install VS Code with Remote SSH (Optional, for Advanced Users)

**What is VS Code Remote SSH?**
Edit code on Raspberry Pi directly from VS Code on Windows - super convenient for debugging!

**Download VS Code:**
1. Go to: https://code.visualstudio.com/
2. Download Windows version
3. Install with default settings

**Install Remote SSH Extension:**
1. Open VS Code
2. Click Extensions icon (left sidebar, squares icon)
3. Search: **Remote - SSH**
4. Click **Install** on "Remote - SSH" by Microsoft
5. Done!

---

## 🔍 Step 2: Find Your Raspberry Pi's IP Address

### Method 1: Using Advanced IP Scanner (Easiest!)

1. **Run Advanced IP Scanner**
2. Click **Scan** (big green button)
3. Wait 30 seconds for scan to complete
4. **Look for device named:**
   - `raspberrypi` or
   - `Raspberry Pi Foundation` (in Manufacturer column)
5. **Note the IP address** (e.g., `192.168.1.150`)

**Screenshot of what to look for:**
```
IP Address       Name              Manufacturer
192.168.1.1      router            TP-Link
192.168.1.100    DESKTOP-ABC       Microsoft
192.168.1.150    raspberrypi       Raspberry Pi Foundation  ← THIS ONE!
```

---

### Method 2: Using Your Router

1. Open browser
2. Go to router admin page:
   - Usually: `192.168.1.1` or `192.168.0.1`
   - Try: `http://192.168.1.1`
3. Login (check router sticker for password)
4. Find "Connected Devices" or "DHCP Clients"
5. Look for "raspberrypi" - note its IP

---

### Method 3: Using Windows Command Prompt

```powershell
# Open PowerShell or Command Prompt
arp -a

# Look for MAC addresses starting with:
# b8-27-eb or dc-a6-32 (Raspberry Pi MAC addresses)
```

---

### Method 4: Connect Monitor to RPi

If all else fails:
1. Connect HDMI monitor to RPi
2. Connect keyboard
3. Power on RPi
4. Login (username: `pi`, password: `raspberry`)
5. Type command:
```bash
hostname -I
```
6. You'll see the IP address!

---

## 🔐 Step 3: Connect Using PuTTY (SSH)

### First Time Connection

1. **Open PuTTY**
2. In "Host Name" box, type: `pi@192.168.1.150` (use YOUR RPi's IP)
3. Port: `22` (default)
4. Connection type: **SSH**
5. Click **Open**

**You'll see a security alert:**
```
PuTTY Security Alert
The server's host key is not cached...
Do you trust this host?
```
6. Click **Yes** (this is normal for first connection)

**Login:**
```
login as: pi
password: raspberry
```
**⚠️ When typing password, you won't see any characters - this is normal! Just type and press Enter.**

**Success!** You should see:
```
Linux raspberrypi 5.10.63-v7l+ #1459 SMP Wed Oct 6 16:41:57 BST 2021 armv7l

pi@raspberrypi:~ $
```

---

### PuTTY Settings to Save

**To save your connection:**
1. Before clicking Open
2. Type a name in "Saved Sessions" (e.g., "My RPi")
3. Click **Save**
4. Next time: Double-click "My RPi" to connect instantly!

**Useful PuTTY Settings:**
- Window → Columns: `120`, Rows: `40` (bigger window)
- Window → Colours → Use system colours: **Uncheck** (better colors)
- Terminal → Bell → **None** (no annoying beeps)

---

## 📁 Step 4: Transfer Files Using WinSCP

### First Time Setup

1. **Open WinSCP**
2. Click **New Site**
3. File protocol: **SFTP**
4. Host name: `192.168.1.150` (YOUR RPi IP)
5. Port: `22`
6. User name: `pi`
7. Password: `raspberry`
8. Click **Save**
9. Give it a name: "My RPi"
10. Click **OK**

### Connect and Transfer Files

1. **Click Login** (or double-click saved session)
2. If asked about host key, click **Yes**

**You'll see two panels:**
- **Left:** Your Windows files
- **Right:** Raspberry Pi files

**Transfer files:**
- **Windows → RPi:** Drag from left to right
- **RPi → Windows:** Drag from right to left
- **Create folder:** Right panel → Right-click → New → Directory
- **Delete file:** Right-click → Delete

**Shortcuts:**
- **F5** - Refresh
- **F6** - Move/Rename
- **Delete** - Delete file
- **Ctrl+Alt+N** - Open PuTTY terminal

---

## 💻 Step 5: Use VS Code for Remote Development (Advanced)

### Setup Remote Connection

1. **Open VS Code**
2. Press **F1** (or Ctrl+Shift+P)
3. Type: `Remote-SSH: Connect to Host`
4. Click it
5. Click **+ Add New SSH Host**
6. Type: `ssh pi@192.168.1.150`
7. Press Enter
8. Select config file: `C:\Users\YourName\.ssh\config` (first option)
9. Click **Connect**

**First time:**
- Select platform: **Linux**
- Trust host: **Continue**
- Enter password: `raspberry`

**Success!** VS Code is now connected to your RPi!

### Edit Files Remotely

1. Click **Explorer** icon (top left)
2. Click **Open Folder**
3. Type: `/home/pi/OctoBoard/rpi_system`
4. Click **OK**
5. Enter password: `raspberry`

**Now you can:**
- ✅ Edit files directly on RPi
- ✅ Save changes (Ctrl+S)
- ✅ Use VS Code's debugging tools
- ✅ Run terminal commands (View → Terminal)

---

## 🐛 Step 6: Debugging on Raspberry Pi

### View Logs in Real-Time

**In PuTTY:**
```bash
# See API server output
# (If running with start_rpi.sh, logs appear in same terminal)

# See system logs
sudo journalctl -f

# See specific service logs (if using systemd)
sudo journalctl -u octoboard -f

# Press Ctrl+C to stop viewing logs
```

### Check What's Running

```bash
# See all Python processes
ps aux | grep python

# Check specific port
sudo lsof -i :8001

# Check if API server is responding
curl http://localhost:8001/status
```

### Debug Connection Issues

**Test if RPi can reach Main PC:**
```bash
# Ping Main PC
ping 192.168.1.100

# Test file receiver
curl http://192.168.1.100:8000/ping
```

**Test if Main PC can reach RPi:**
```powershell
# In Windows PowerShell
curl http://192.168.1.150:8001/status
```

### View Python Errors

**In PuTTY (while API server is running):**
- All errors appear in the terminal
- Look for lines starting with:
  - `ERROR:`
  - `Traceback:`
  - `Exception:`

**Copy error messages:**
- Select text with mouse in PuTTY
- Text is automatically copied!
- Right-click in any program to paste

---

## 🔧 Common Debugging Tasks

### Check I2C Devices

```bash
# See connected I2C devices
sudo i2cdetect -y 1

# Should show Octoboard addresses:
# 20 (MCP23017), 48 (ADS1115), 60-61 (MCP4728)
```

### Test Python Code

```bash
# Activate virtual environment
cd /home/pi/rpi_system
source venv/bin/activate

# Run Python commands
python3 -c "print('Hello from RPi!')"

# Test hardware detection
python3 -c "
from software import get_hardware_classes
OBoardManager, _, _, _ = get_hardware_classes()
manager = OBoardManager(i2c_num=1)
print(f'Found {len(manager.oboards)} boards')
"
```

### Edit Configuration Files

**Using nano (built-in text editor):**
```bash
# Edit constants file
nano software/hardware/constants.py

# Navigate: Arrow keys
# Save: Ctrl+O → Enter
# Exit: Ctrl+X
```

**Or use WinSCP:**
1. Navigate to file in right panel
2. Right-click → Edit
3. Edit in Notepad
4. Save (Ctrl+S)
5. Close Notepad
6. WinSCP uploads automatically!

---

## 🎯 Recommended Workflow

### For Debugging:

1. **PuTTY (Terminal 1)** - Run API server
   ```bash
   cd /home/pi/rpi_system
   source venv/bin/activate
   ./start_rpi.sh
   ```

2. **PuTTY (Terminal 2)** - For commands/debugging
   - Open another PuTTY connection
   - Run test commands
   - Check logs
   - Monitor system

3. **WinSCP** - Transfer/edit files
   - Drag files to RPi
   - Quick edits
   - View logs

4. **VS Code** (Optional) - For heavy coding
   - Edit multiple files
   - Search/replace across project
   - Git integration
   - Debugging tools

---

## 📝 Quick Reference Commands

### Connection Commands

```powershell
# Windows PowerShell - Ping RPi
ping 192.168.1.150

# Windows PowerShell - SSH (if you have OpenSSH)
ssh pi@192.168.1.150

# Windows PowerShell - Copy files
scp -r C:\OctoBoard\rpi_system pi@192.168.1.150:/home/pi/
```

### RPi Commands

```bash
# Basic navigation
pwd              # Print current directory
ls               # List files
cd foldername    # Change directory
cd ..            # Go up one level
cd ~             # Go to home directory

# File operations
cat filename     # View file content
nano filename    # Edit file
cp file1 file2   # Copy file
mv old new       # Move/rename
rm filename      # Delete file

# System
sudo reboot      # Restart RPi
sudo shutdown -h now  # Shutdown
exit             # Logout

# Network
hostname -I      # Show IP address
ifconfig         # Network info
ping google.com  # Test internet
```

---

## 🆘 Troubleshooting

### Can't Connect with PuTTY

**Error: "Network error: Connection refused"**
- RPi not powered on
- Wrong IP address
- SSH not enabled on RPi

**Solution:**
```bash
# Enable SSH (need monitor/keyboard on RPi)
sudo raspi-config
# → Interface Options → SSH → Enable
```

**Or create SSH file:**
1. Remove SD card from RPi
2. Insert into Windows PC
3. Open boot drive
4. Create empty file named `ssh` (no extension)
5. Put SD card back in RPi

---

### Can't Transfer Files with WinSCP

**Error: "Authentication failed"**
- Wrong password
- SSH not enabled

**Error: "Permission denied"**
- Create folder in `/home/pi/` not `/root/`
- Or use: `sudo chown -R pi:pi /path/to/folder`

---

### Lost RPi IP Address

**Quick way to find it again:**
1. Open Advanced IP Scanner
2. Click Scan
3. Look for "raspberrypi"

**Or check router's DHCP list**

---

## 📚 Useful Resources

**PuTTY Documentation:**
- https://www.putty.org/

**WinSCP Guide:**
- https://winscp.net/eng/docs/start

**Raspberry Pi SSH:**
- https://www.raspberrypi.com/documentation/computers/remote-access.html

**VS Code Remote SSH:**
- https://code.visualstudio.com/docs/remote/ssh

---

## ✅ You're Ready!

**You now have:**
- ✅ PuTTY - Control RPi via command line
- ✅ WinSCP - Transfer files easily
- ✅ IP Scanner - Find RPi on network
- ✅ VS Code (optional) - Professional editing

**Start here:** Follow `RPi_BEGINNER_GUIDE.md` with these tools!

**Need help?**
- PuTTY is your main tool for running commands
- WinSCP for moving files
- VS Code for editing code remotely (advanced)

🎉 **Happy Raspberry Pi coding!**

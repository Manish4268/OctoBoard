# 🚀 Getting Started with OctoBoard v2.0

**Welcome!** This guide will get you up and running in 5 minutes.

---

## What You Have

A complete distributed system for testing 288 solar cell channels:
- **3 Raspberry Pis** (can simulate on Windows)
- **Main PC dashboard** for control and monitoring
- **Automated hourly measurements** with file transfer
- **Web interface** for easy operation

---

## Installation (First Time Only)

### Prerequisites
- Windows 10/11
- Python 3.9 or higher
- Web browser

### Step 1: Install Main PC System

Open PowerShell:

```powershell
cd C:\Users\ManishJadhav\OctoBoard\main_pc_system

# The start script will automatically:
# - Create virtual environment
# - Install all dependencies
# - Start both services
.\start.bat
```

**Expected:** Two terminal windows open + browser opens dashboard

### Step 2: Install RPi System (Simulation)

Open **new** PowerShell window:

```powershell
cd C:\Users\ManishJadhav\OctoBoard\rpi_system

# Run startup script
.\start.bat

# When asked: "Run in SIMULATION mode? (y/n):"
# Type: y
```

**Expected:** RPi API server starts in simulation mode

---

## First Measurement (5 Minutes)

### Step 1: Open Dashboard

Browser should automatically open to: **http://localhost:8501**

If not, manually open: http://localhost:8501

### Step 2: Check System Status

Look at the **left sidebar**:
- ✅ File Receiver should show "Online" (green)
- ✅ RPi 1 should show "Online" (green)

If red, click "🔄 Refresh Status" button

### Step 3: Start a Test Measurement

1. Click **"📝 New Measurement"** tab (at top)

2. Fill in **Sample Information:**
   - Sample ID: `Test_001`
   - Cell Area: `0.09` (leave default)
   - Current Limit: `50` (leave default)

3. Fill in **IV Sweep Parameters:**
   - All default values are fine for testing

4. Under **Hardware Assignment:**
   - Select Raspberry Pi: `RPi 1`
   - Select Channel Slot: `Slot 0: Channels 0-3`

5. Click **"🚀 Start Measurement"** button

**Expected:**
- Success message appears
- Green checkmark with details
- Message: "Data folder created"

### Step 4: Verify Active Measurement

1. Click **"📊 Active Measurements"** tab

2. You should see:
   - RPi 1 section
   - 📦 Test_001
   - Channels: 0-3
   - 🟢 Running
   - ⏹️ Stop button

### Step 5: Trigger First IV Sweep

**Option A: Wait 1 Hour** (normal operation)
- System will automatically run IV sweep after 1 hour

**Option B: Test Immediately** (modify temporarily)

In the RPi terminal, press `Ctrl+C` to stop.

Edit `rpi_system/api_server.py`:
```python
# Line ~250, find:
schedule.every(IV_SWEEP_INTERVAL_HOURS).hours.do(run_hourly_iv_sweeps)

# Change to:
schedule.every(10).seconds.do(run_hourly_iv_sweeps)
```

Restart: `python api_server.py`

Now IV sweep runs every 10 seconds instead!

### Step 6: Check Generated Files

After sweep runs (watch RPi terminal for messages):

```powershell
dir C:\OctoBoard_Data\Test_001\a\
```

**Expected:** CSV files like `IV_20240101_120530.csv`

### Step 7: Visualize Data

1. In dashboard, click **"📈 Data Visualization"** tab

2. Select Sample: `Test_001`

3. Select Pixel: `a`

4. Select latest CSV file

5. **See beautiful IV and Power curves!**

### Step 8: Stop Measurement

1. Go to **"📊 Active Measurements"** tab

2. Find `Test_001`

3. Click **"⏹️ Stop"** button

4. Confirm it disappears from active list

---

## Understanding the Dashboard

### 🏠 Sidebar (Left)
- **System Status** - Green = good, Red = problem
- **RPi List** - Shows all 3 Raspberry Pis
- **Active Samples** - Total count across all RPis
- **🔄 Refresh** - Update all statuses

### 📝 New Measurement Tab
- Configure new samples
- Assign to RPi and channel slot
- Start measurements

### 📊 Active Measurements Tab
- See all running measurements
- Stop measurements
- Real-time status

### 📁 Data Browser Tab
- Browse all samples
- See file counts per pixel
- Check latest files

### 📈 Data Visualization Tab
- Plot IV curves
- Plot Power curves
- See key metrics (Max Power, Voltage @ MPP)
- View raw data

---

## Understanding the Data

### Where Files Are Stored

```
C:\OctoBoard_Data\
└── Test_001\          ← Your Sample ID
    ├── a\             ← Pixel a (channel 0)
    │   └── IV_timestamp.csv
    ├── b\             ← Pixel b (channel 1)
    ├── c\             ← Pixel c (channel 2)
    └── d\             ← Pixel d (channel 3)
```

### CSV File Format

Each file contains IV sweep data:

```csv
voltage,current,power,timestamp
0.000,0.0450,0.0000,2024-01-01T12:05:30
0.010,0.0449,0.0004,2024-01-01T12:05:30
0.020,0.0448,0.0009,2024-01-01T12:05:30
...
1.200,0.0201,0.0241,2024-01-01T12:05:42
```

Columns:
- **voltage** - Applied voltage (V)
- **current** - Measured current (A)
- **power** - Calculated power (W) = voltage × current
- **timestamp** - When measurement taken

---

## System Capacity

| Metric | Value |
|--------|-------|
| Total Channels | 288 |
| Channels per RPi | 96 |
| Samples per RPi | 24 |
| Total Sample Capacity | 72 |
| Pixels per Sample | 4 (a, b, c, d) |
| Files Generated | 96/hour/RPi (288/hour total) |

---

## Common Questions

### Q: Do I need internet?
**A:** No! System works on local network (LAN) only.

### Q: Can I test without Raspberry Pi?
**A:** Yes! Use simulation mode (what you just did).

### Q: How do I add more samples?
**A:** Click "New Measurement" tab, use different Sample ID, select available slot.

### Q: What if I close the dashboard?
**A:** Just reopen browser to http://localhost:8501 - measurements keep running!

### Q: How do I stop everything?
**A:** Close both terminal windows (File Receiver and RPi API).

### Q: Where are the logs?
**A:** Check terminal windows for real-time logs.

### Q: Can I run multiple RPis?
**A:** Yes! Start multiple instances on different ports (8001, 8002, 8003).

---

## Next Steps

### For Development
- ✅ Tested simulation mode
- 📖 Read [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing
- 🔧 Modify IV parameters in dashboard
- 📊 Test with multiple samples

### For Production
- 📖 Read [main_pc_system/README.md](main_pc_system/README.md)
- 📖 Read [rpi_system/README.md](rpi_system/README.md)
- 🔧 Configure network (static IPs)
- 🔌 Deploy to actual Raspberry Pis
- 🧪 Test with real hardware
- ⚙️ Setup as system services

---

## Troubleshooting

### Dashboard Shows "File Receiver Offline" (Red)

**Solution:**
```powershell
# Check if running
curl http://localhost:8000/ping

# If not, start it
cd main_pc_system
.\start_receiver.bat
```

### Dashboard Shows "RPi 1 Offline" (Red)

**Solution:**
```powershell
# Check if running
curl http://localhost:8001/status

# If not, start it
cd rpi_system
.\start.bat
```

### No Files Appearing

**Solution:**
1. Check RPi terminal - did sweep run?
2. Check file receiver terminal - any errors?
3. Verify: `dir C:\OctoBoard_Data\Test_001\`
4. Try manually triggering sweep (10-second interval trick above)

### "No Available Slots" Error

**Solution:**
- All 24 slots occupied on that RPi
- Stop some measurements or select different RPi

---

## Quick Command Reference

```powershell
# Start everything
cd main_pc_system ; .\start.bat
cd rpi_system ; .\start.bat

# Check status
curl http://localhost:8000/ping          # File receiver
curl http://localhost:8001/status        # RPi 1

# View data
dir C:\OctoBoard_Data\                   # All samples
dir C:\OctoBoard_Data\Test_001\a\        # Specific pixel

# Test file receiver
curl -X POST http://localhost:8000/upload
```

---

## Documentation Index

| Document | Purpose |
|----------|---------|
| **This file** | Quick 5-minute start |
| [readme.md](readme.md) | Full project overview |
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | Complete testing procedures |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | System architecture |
| [main_pc_system/README.md](main_pc_system/README.md) | Main PC setup & API |
| [rpi_system/README.md](rpi_system/README.md) | RPi setup & configuration |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | What was built |

---

## Support

Having issues?
1. Check terminal logs for error messages
2. Review troubleshooting section above
3. Read [TESTING_GUIDE.md](TESTING_GUIDE.md)
4. Check if ports are in use: `netstat -ano | findstr :8000`

---

## Success! 🎉

You've successfully:
- ✅ Installed OctoBoard v2.0
- ✅ Started main PC system
- ✅ Simulated a Raspberry Pi
- ✅ Configured and started a measurement
- ✅ Triggered an IV sweep
- ✅ Viewed generated data files
- ✅ Visualized IV curves

**You're ready to use OctoBoard!**

---

*Last Updated: January 2024*
*Version: 2.0*

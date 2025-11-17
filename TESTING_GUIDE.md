# OctoBoard System - Complete Testing Guide

## Overview

This guide walks you through testing the complete OctoBoard system in **simulation mode** on Windows, without requiring Raspberry Pi hardware.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Main PC (192.168.1.100)              │
│  ┌─────────────────┐         ┌──────────────────────┐  │
│  │  File Receiver  │         │   Streamlit          │  │
│  │  Port: 8000     │◄────────┤   Dashboard          │  │
│  └────────▲────────┘         │   Port: 8501         │  │
│           │                  └──────────────────────┘  │
└───────────┼──────────────────────────────────────────────┘
            │
            │ HTTP POST (File Transfer)
            │
    ┌───────┴────────┬──────────────────┬────────────────┐
    │                │                  │                │
┌───▼────────┐  ┌────▼──────┐    ┌─────▼───────┐       │
│  RPi 1     │  │  RPi 2    │    │   RPi 3     │       │
│  .101:8001 │  │  .102:8001│    │   .103:8001 │       │
│            │  │           │    │             │       │
│ 96 chs     │  │ 96 chs    │    │ 96 chs      │       │
│ 24 samples │  │ 24 samples│    │ 24 samples  │       │
└────────────┘  └───────────┘    └─────────────┘       │
```

## Prerequisites

- Windows 10/11
- Python 3.9+
- PowerShell or Command Prompt
- Web browser

## Test Environment Setup

### Step 1: Install Main PC System

```powershell
# Navigate to main_pc_system
cd C:\Users\ManishJadhav\OctoBoard\main_pc_system

# Run startup script (will create venv and install deps)
.\start.bat
```

**Expected:** Two terminal windows open:
- "OctoBoard File Receiver" - Shows uvicorn server logs
- "OctoBoard Dashboard" - Opens browser at http://localhost:8501

### Step 2: Verify Main PC Services

**Test File Receiver:**
```powershell
curl http://localhost:8000/ping
```

**Expected Response:**
```json
{"status": "ok", "message": "File receiver is running"}
```

**Test Dashboard:**
- Open browser to `http://localhost:8501`
- Should see "OctoBoard Control Center" title
- Sidebar shows "File Receiver Online" with green checkmark

## Simulating Raspberry Pis

### Step 3: Start Simulated RPi 1

Open **new PowerShell terminal**:

```powershell
cd C:\Users\ManishJadhav\OctoBoard\rpi_system

# Create venv and install
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Set simulation mode
$env:OCTOBOARD_SIMULATION="True"

# Start API server
python api_server.py
```

**Expected Output:**
```
========================================
OctoBoard RPi API Server
========================================
Mode: SIMULATION
Total Boards: 12
Total Channels: 96
...
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### Step 4: Verify RPi API

In **another terminal**:

```powershell
curl http://localhost:8001/status
```

**Expected Response:**
```json
{
  "status": "online",
  "total_channels": 96,
  "total_samples_capacity": 24,
  "active_samples": 0,
  "available_slots": 24
}
```

### Step 5: Check Dashboard Connection

1. Go to dashboard at `http://localhost:8501`
2. Click "🔄 Refresh Status" in sidebar
3. Should show "✅ RPi 1" with green status

⚠️ **Note:** If using localhost (127.0.0.1) for testing, you need to modify IP addresses:

**Option A: Use localhost for testing**
Edit `rpi_system/api_server.py`:
```python
MAIN_PC_IP = "127.0.0.1"  # Changed from 192.168.1.100
```

Edit `main_pc_system/dashboard.py`:
```python
RPIS = {
    "RPi 1": {"url": "http://127.0.0.1:8001", "id": "rpi_1"},
}
```

**Option B: Configure actual network IPs** (skip for basic testing)

## End-to-End Testing

### Test 1: Start a Measurement

1. **In Dashboard** → Go to "📝 New Measurement" tab

2. **Fill Sample Info:**
   - Sample ID: `Test_Sample_001`
   - Cell Area: `0.09` cm²
   - Current Limit: `50` mA

3. **Configure IV Sweep:**
   - Start Voltage: `0.0` V
   - Stop Voltage: `1.2` V
   - Voltage Step: `0.01` V
   - Settle Time: `0.1` s

4. **Select Hardware:**
   - Raspberry Pi: `RPi 1`
   - Channel Slot: `Slot 0: Channels 0-3` (or any available)

5. **Click "🚀 Start Measurement"**

**Expected:**
- Success message appears
- Shows assigned channels and configuration
- Folder created: `C:\OctoBoard_Data\Test_Sample_001\`
- With subfolders: `a/`, `b/`, `c/`, `d/`

### Test 2: Verify Active Measurement

1. **In Dashboard** → Go to "📊 Active Measurements" tab

2. **Check RPi 1 section:**
   - Should show `Test_Sample_001`
   - Status: "🟢 Running"
   - Channels: 0-3

### Test 3: Manual IV Sweep Trigger

In RPi terminal, you should see scheduled tasks:
```
INFO: Scheduled hourly IV sweep for Test_Sample_001
INFO: Next run at: 2024-01-01 13:00:00
```

To **manually trigger** IV sweep (for testing):

```powershell
# In RPi terminal, press Ctrl+C to stop
# Then modify api_server.py temporarily:

# Find this line:
schedule.every(IV_SWEEP_INTERVAL_HOURS).hours.do(run_hourly_iv_sweeps)

# Change to:
schedule.every(10).seconds.do(run_hourly_iv_sweeps)

# Restart:
python api_server.py
```

Now IV sweep will run every 10 seconds instead of every hour.

**Expected Behavior:**
1. RPi runs IV sweep on all 4 pixels (a, b, c, d)
2. Generates 4 CSV files
3. Transfers files to Main PC
4. Main PC saves to `C:\OctoBoard_Data\Test_Sample_001\{pixel}\`

### Test 4: Verify File Transfer

**Check RPi Logs:**
```
INFO: Running IV sweep for Test_Sample_001 (channels 0-3)
INFO: Pixel a: IV sweep complete, 121 points
INFO: Transferring file to Main PC...
INFO: Transfer successful: Test_Sample_001/a/IV_20240101_120530.csv
...
```

**Check File Receiver Logs:**
```
INFO: Received file upload: Test_Sample_001/a/IV_20240101_120530.csv
INFO: File saved successfully (12345 bytes)
```

**Check File System:**
```powershell
dir C:\OctoBoard_Data\Test_Sample_001\a\
```

Should show CSV files with timestamps.

### Test 5: Browse Data in Dashboard

1. **Dashboard** → "📁 Data Browser" tab
2. Select `Test_Sample_001` from dropdown
3. Should show all 4 pixels (a, b, c, d)
4. Each pixel should show file count
5. Latest file timestamp displayed

### Test 6: Visualize IV Curves

1. **Dashboard** → "📈 Data Visualization" tab
2. Select `Test_Sample_001`
3. Choose pixel (e.g., `a`)
4. Select most recent file
5. Should display:
   - IV Curve (Voltage vs Current)
   - Power Curve (Voltage vs Power)
   - Key metrics (Max Power, Voltage at MPP)

**Expected Plot:**
- Current increases with voltage (typical solar cell behavior)
- Power curve shows peak (maximum power point)
- Metrics calculated correctly

### Test 7: Stop Measurement

1. **Dashboard** → "📊 Active Measurements" tab
2. Find `Test_Sample_001`
3. Click "⏹️ Stop" button
4. Confirmation appears
5. Sample removed from active list

**Check RPi Logs:**
```
INFO: Stopping measurement for Test_Sample_001
INFO: Channels 0-3 released
INFO: Scheduler job removed
```

## Multi-RPi Testing (Optional)

### Start Multiple Simulated RPis

**Terminal 2 - RPi 2:**
```powershell
cd C:\Users\ManishJadhav\OctoBoard\rpi_system
.\venv\Scripts\Activate.ps1
$env:OCTOBOARD_SIMULATION="True"
$env:RPI_PORT="8002"  # Different port for local testing
python api_server.py
```

**Terminal 3 - RPi 3:**
```powershell
cd C:\Users\ManishJadhav\OctoBoard\rpi_system
.\venv\Scripts\Activate.ps1
$env:OCTOBOARD_SIMULATION="True"
$env:RPI_PORT="8003"  # Different port for local testing
python api_server.py
```

**Update Dashboard URLs:**
Edit `main_pc_system/dashboard.py`:
```python
RPIS = {
    "RPi 1": {"url": "http://127.0.0.1:8001", "id": "rpi_1"},
    "RPi 2": {"url": "http://127.0.0.1:8002", "id": "rpi_2"},
    "RPi 3": {"url": "http://127.0.0.1:8003", "id": "rpi_3"},
}
```

Restart dashboard to see all 3 RPis online.

## Common Issues & Solutions

### Issue 1: File Receiver Shows Offline

**Symptoms:** Red "❌ File Receiver Offline" in dashboard sidebar

**Solution:**
```powershell
# Check if receiver is running
curl http://localhost:8000/ping

# If not responding, restart:
cd main_pc_system
.\start_receiver.bat
```

### Issue 2: RPi Shows Offline in Dashboard

**Symptoms:** Red "❌ RPi 1 (Offline)"

**Solutions:**
1. Check RPi terminal - is server running?
2. Verify URLs in dashboard.py match RPi ports
3. Test RPi endpoint directly:
   ```powershell
   curl http://localhost:8001/status
   ```

### Issue 3: Files Not Appearing

**Symptoms:** IV sweep runs but no files in data folder

**Check:**
1. File receiver logs - any errors?
2. RPi logs - did transfer succeed?
3. Folder permissions on `C:\OctoBoard_Data\`
4. Main PC IP configured correctly in RPi

**Debug:**
```powershell
# Check receiver stats
curl http://localhost:8000/stats

# Should show files_received > 0
```

### Issue 4: "No Available Slots" Error

**Symptoms:** Cannot start measurement, all slots occupied

**Solution:**
Stop existing measurements or restart RPi server:
```powershell
# In RPi terminal, press Ctrl+C
# Restart:
python api_server.py
```

### Issue 5: Import Errors

**Symptoms:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```powershell
# Activate venv and reinstall
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Performance Testing

### Test Data Generation Rate

**Measure files per minute:**
```powershell
# Get initial count
$before = (Get-ChildItem C:\OctoBoard_Data\Test_Sample_001\a\).Count

# Wait 1 minute (with 10-second interval)

# Get final count
$after = (Get-ChildItem C:\OctoBoard_Data\Test_Sample_001\a\).Count

# Calculate rate
$rate = $after - $before
Write-Host "Files per minute: $rate"
```

**Expected:** 6 files/minute (10-second interval)

### Test Dashboard Responsiveness

1. Start 10+ measurements across RPis
2. Navigate between tabs
3. Refresh status multiple times
4. Check lag or delays

**Expected:** < 2 seconds for page loads

## Data Validation

### Verify IV Curve Quality

Open generated CSV file:
```powershell
notepad C:\OctoBoard_Data\Test_Sample_001\a\IV_<timestamp>.csv
```

**Check:**
- Voltage range: 0.0 V to 1.2 V
- Voltage steps: ~0.01 V intervals
- Current values: Reasonable (0-50 mA)
- No NaN or null values
- Power = voltage × current

**Sample Data:**
```csv
voltage,current,power,timestamp
0.000,0.0450,0.0000,2024-01-01T12:05:30
0.010,0.0449,0.0004,2024-01-01T12:05:30
0.020,0.0448,0.0009,2024-01-01T12:05:30
...
```

## System Limits Testing

### Test Maximum Capacity

1. Start 24 measurements on RPi 1 (all slots)
2. Verify dashboard shows "24/24" active
3. Try starting 25th measurement
4. Should show "No available slots" error

### Test File Transfer Under Load

1. Configure all 3 RPis with 10-second sweep interval
2. Start 24 samples on each RPi
3. Wait for sweeps to execute simultaneously
4. Monitor file receiver logs

**Expected:**
- 288 files transferred (72 samples × 4 pixels)
- All transfers succeed
- No timeouts or errors

## Production Deployment Testing

### Test on Actual Network

1. Configure Main PC with static IP: `192.168.1.100`
2. Configure RPis with IPs: `.101`, `.102`, `.103`
3. Update `api_server.py` and `dashboard.py` with real IPs
4. Test connectivity:
   ```bash
   # From Main PC
   ping 192.168.1.101
   curl http://192.168.1.101:8001/status
   ```

### Test Hardware Mode

On actual Raspberry Pi:
```bash
cd /home/pi/OctoBoard/rpi_system

# DO NOT set OCTOBOARD_SIMULATION
python api_server.py
```

Should connect to real hardware (MCP4728, ADS1115, etc.)

## Automated Testing Script

Save as `test_system.ps1`:

```powershell
# OctoBoard System Test Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "OctoBoard System Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Test 1: File Receiver
Write-Host "`n[Test 1] Checking File Receiver..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/ping"
    Write-Host "✅ PASS: File Receiver online" -ForegroundColor Green
} catch {
    Write-Host "❌ FAIL: File Receiver offline" -ForegroundColor Red
    exit 1
}

# Test 2: RPi 1
Write-Host "`n[Test 2] Checking RPi 1..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/status"
    Write-Host "✅ PASS: RPi 1 online ($($response.total_channels) channels)" -ForegroundColor Green
} catch {
    Write-Host "❌ FAIL: RPi 1 offline" -ForegroundColor Red
    exit 1
}

# Test 3: Data Directory
Write-Host "`n[Test 3] Checking Data Directory..." -ForegroundColor Yellow
if (Test-Path "C:\OctoBoard_Data") {
    Write-Host "✅ PASS: Data directory exists" -ForegroundColor Green
} else {
    Write-Host "❌ FAIL: Data directory missing" -ForegroundColor Red
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "All tests passed! ✅" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
```

Run:
```powershell
.\test_system.ps1
```

## Success Criteria

Complete system is working correctly when:

- ✅ File receiver responds to /ping
- ✅ All RPis show "Online" in dashboard
- ✅ Can start new measurements
- ✅ IV sweeps execute on schedule
- ✅ Files transfer automatically to Main PC
- ✅ Files appear in correct folder structure
- ✅ Dashboard displays all active measurements
- ✅ Data visualization plots IV curves correctly
- ✅ Can stop measurements cleanly
- ✅ System handles 72 concurrent samples

## Next Steps

After successful testing:

1. **Configure Production Network**: Set static IPs on Main PC and RPis
2. **Deploy to Hardware**: Transfer code to Raspberry Pis
3. **Test with Real Hardware**: Verify MCP4728, ADS1115 connections
4. **Calibration**: Adjust voltage/current ranges for actual cells
5. **Long-term Testing**: Run 24+ hour test to verify stability
6. **Backup Strategy**: Implement automated data backup

## Support

If tests fail, check:
- Terminal logs for error messages
- Network connectivity
- Port availability
- Python dependencies
- File permissions

For persistent issues, review code in:
- `rpi_system/api_server.py`
- `main_pc_system/file_receiver.py`
- `main_pc_system/dashboard.py`

# OctoBoard System Summary

## ✅ System Configuration (Updated)

### Data Storage Location
**Main PC Storage Path:**
```
C:\Users\ManishJadhav\SynologyDrive\Rayleigh\Outdoor Data
```

### Folder Structure
```
Outdoor Data/
├── 1234/                          # Sample ID folder
│   ├── Config.txt                 # Measurement configuration
│   ├── a/                         # Pixel a data
│   │   ├── IV_2025-11-17_10-00-00.csv
│   │   ├── IV_2025-11-17_11-00-00.csv
│   │   └── ...
│   ├── b/                         # Pixel b data
│   │   └── IV_*.csv
│   ├── c/                         # Pixel c data
│   │   └── IV_*.csv
│   └── d/                         # Pixel d data
│       └── IV_*.csv
└── 5678/                          # Another sample
    ├── Config.txt
    ├── a/, b/, c/, d/
    └── ...
```

## 📋 Config.txt Format
Each sample folder contains a `Config.txt` file with measurement parameters:
```
Sample ID: 1234
RPI ID: rpi_1
Start Channel: 0
Channels Used: 0 to 3
Cell Area: 1.0 cm²
Current Limit: 50.0 mA
Start Voltage: -0.5 V
Stop Voltage: 1.2 V
Voltage Step: 0.01 V
Settle Time: 0.05 s
Measurement Type: iv_sweep
Started: 2025-11-17 10:00:00
IV Sweep Interval: Every 1 hour(s)
```

## 🔄 How It Works

### 1. Start a Measurement
- Go to dashboard: http://localhost:8501
- Navigate to "📝 New Measurement" tab
- Fill in Sample ID and IV parameters
- Select RPi and Slot (0-23)
- Click "Start Measurement"

### 2. What Happens Next
1. **Config.txt Created**: RPi creates `Config.txt` with all measurement parameters
2. **Initial IV Sweep**: RPi immediately performs first IV sweep for all 4 pixels (a, b, c, d)
3. **Data Transfer**: All files (Config.txt + 4 IV CSV files) are transferred to Main PC
4. **Hourly Repeats**: Every 1 hour, RPi automatically:
   - Performs IV sweep for all 4 pixels
   - Generates 4 new CSV files (one per pixel)
   - Transfers them to Main PC

### 3. File Naming
- **Config**: `Config.txt` (created once at start)
- **IV Data**: `IV_YYYY-MM-DD_HH-MM-SS.csv` (one per pixel per hour)

### 4. IV Data CSV Format
```csv
timestamp,voltage,current,power
2025-11-17T10:00:00,0.0,0.0,0.0
2025-11-17T10:00:01,0.1,0.001,0.0001
...
```

## 🖥️ System Architecture

### Components Running:
1. **Main PC Dashboard** (Streamlit)
   - URL: http://localhost:8501
   - Port: 8501
   - Purpose: Web UI for system control

2. **Main PC File Receiver** (FastAPI)
   - URL: http://localhost:8000
   - Port: 8000
   - Purpose: Receives files from RPis

3. **RPi 1 API Server** (FastAPI) - Currently Simulated
   - URL: http://localhost:8001
   - Port: 8001
   - Purpose: Controls 96 channels, performs measurements

### Network Configuration
**For Testing (Current Setup):**
- Dashboard: `localhost:8501`
- File Receiver: `localhost:8000`
- RPi 1-3: `localhost:8001-8003`

**For Production (Actual Hardware):**
- Main PC: `192.168.1.100`
- RPi 1: `192.168.1.101:8001`
- RPi 2: `192.168.1.102:8001`
- RPi 3: `192.168.1.103:8001`

## 📊 System Capacity

| Component | Specification |
|-----------|--------------|
| Total RPis | 3 |
| Channels per RPi | 96 (12 Octoboards × 8 channels) |
| Total Channels | 288 |
| Samples per RPi | 24 (1 sample = 4 pixels = 4 channels) |
| Total Samples | 72 |
| Pixels per Sample | 4 (a, b, c, d) |
| IV Sweep Interval | Every 1 hour |
| Files per Sample per Hour | 4 (one per pixel) |

## 🚀 Quick Start Commands

### Start Main PC Systems:
```powershell
# Terminal 1: Dashboard
cd main_pc_system
.\venv\Scripts\Activate.ps1
streamlit run dashboard.py

# Terminal 2: File Receiver
cd main_pc_system
.\venv\Scripts\Activate.ps1
python file_receiver.py
```

### Start RPi Systems (Simulated):
```powershell
# Terminal 3: RPi 1
cd rpi_system
.\venv\Scripts\Activate.ps1
$env:OCTOBOARD_SIMULATION="True"
python api_server.py
```

### Access Dashboard:
Open browser: http://localhost:8501

## ✅ Current Status

- [x] Data path changed to `C:/Users/ManishJadhav/SynologyDrive/Rayleigh/Outdoor Data`
- [x] Config.txt auto-generation implemented
- [x] Folder structure: `SampleID/a/`, `SampleID/b/`, `SampleID/c/`, `SampleID/d/`
- [x] Config.txt stored in sample root folder
- [x] Hourly IV sweep scheduler active
- [x] File transfer to Main PC implemented
- [x] Dashboard connected to RPi 1 (simulated)
- [ ] File receiver not yet started
- [ ] Test complete measurement workflow
- [ ] Verify hourly automation

## 🔧 Next Steps

1. **Start File Receiver**: Run `file_receiver.py` on Main PC
2. **Start Test Measurement**: Use dashboard to configure and start a sample
3. **Verify Files**: Check that Config.txt and IV files appear in SynologyDrive folder
4. **Test Hourly Sweep**: Wait or modify interval to test automation
5. **Visualize Data**: Use "Data Visualization" tab to plot IV curves

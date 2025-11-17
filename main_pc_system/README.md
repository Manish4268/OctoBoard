# OctoBoard Main PC System

Control center for managing 3 Raspberry Pis with 288 channels (72 samples) for solar cell testing.

## System Overview

- **Total Capacity**: 3 RPis × 96 channels = 288 channels
- **Sample Capacity**: 72 samples (24 per RPi, 4 pixels per sample)
- **Data Generation**: Hourly IV sweeps per channel (96 files/hour/RPi)
- **Communication**: LAN-based REST API (192.168.1.x network)

## Components

### 1. File Receiver (`file_receiver.py`)
FastAPI server that receives IV measurement files from RPis.

**Features:**
- HTTP POST endpoint for file uploads
- Automatic directory structure creation
- File validation and statistics tracking
- Sample management endpoints

**Endpoints:**
- `POST /upload` - Receive IV files from RPis
- `GET /ping` - Health check
- `GET /stats` - Get receiver statistics
- `GET /samples` - List all samples
- `GET /sample/{sample_id}` - Get files for specific sample

### 2. Dashboard (`dashboard.py`)
Streamlit-based web interface for system control and monitoring.

**Features:**
- Real-time RPi status monitoring
- New sample measurement configuration
- Active measurement management
- Data browser with file listings
- IV curve visualization with Plotly

**Tabs:**
1. **New Measurement** - Configure and start new sample measurements
2. **Active Measurements** - Monitor and control running measurements
3. **Data Browser** - Browse stored IV files by sample/pixel
4. **Data Visualization** - Plot IV and power curves

## Installation

### Requirements
- Python 3.9 or higher
- Windows 10/11 (or Linux/Mac with path adjustments)

### Setup

```powershell
# Navigate to main_pc_system directory
cd C:\Users\ManishJadhav\OctoBoard\main_pc_system

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

## Running the System

### 1. Start File Receiver

```powershell
# Terminal 1
cd C:\Users\ManishJadhav\OctoBoard\main_pc_system
.\venv\Scripts\Activate.ps1
python -m uvicorn file_receiver:app --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Start Dashboard

```powershell
# Terminal 2 (new terminal)
cd C:\Users\ManishJadhav\OctoBoard\main_pc_system
.\venv\Scripts\Activate.ps1
streamlit run dashboard.py
```

**Expected Output:**
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
Network URL: http://192.168.1.100:8501
```

## Network Configuration

### Main PC
- **IP Address**: `192.168.1.100`
- **File Receiver**: Port `8000`
- **Dashboard**: Port `8501`

### Raspberry Pis
- **RPi 1**: `192.168.1.101:8001` (Channels 0-95, Samples 1-24)
- **RPi 2**: `192.168.1.102:8001` (Channels 0-95, Samples 25-48)
- **RPi 3**: `192.168.1.103:8001` (Channels 0-95, Samples 49-72)

## Data Storage

### Directory Structure
```
C:/OctoBoard_Data/
├── Sample_001/
│   ├── a/
│   │   ├── IV_20240101_120000.csv
│   │   ├── IV_20240101_130000.csv
│   │   └── ...
│   ├── b/
│   ├── c/
│   └── d/
├── Sample_002/
│   ├── a/
│   ├── b/
│   ├── c/
│   └── d/
└── ...
```

### File Format
Each IV file is a CSV with columns:
- `voltage` - Applied voltage (V)
- `current` - Measured current (A)
- `power` - Calculated power (W)
- `timestamp` - Measurement timestamp

## Usage Guide

### Starting a New Measurement

1. Open dashboard at `http://localhost:8501`
2. Go to **"New Measurement"** tab
3. Fill in sample information:
   - Sample ID (unique identifier)
   - Cell area (cm²)
   - Current limit (mA)
4. Configure IV sweep parameters:
   - Start/Stop voltage
   - Voltage step
   - Settle time
5. Select RPi and channel slot
6. Click **"Start Measurement"**

### Monitoring Active Measurements

1. Go to **"Active Measurements"** tab
2. View all running measurements across RPis
3. Stop measurements using **"Stop"** button

### Browsing Data

1. Go to **"Data Browser"** tab
2. Select sample from dropdown
3. View file counts for each pixel (a, b, c, d)
4. See latest file timestamps

### Visualizing Data

1. Go to **"Data Visualization"** tab
2. Select sample and pixel
3. Choose specific IV file to plot
4. View IV curve and power curve
5. See key metrics (max power, voltage at MPP)

## Troubleshooting

### File Receiver Not Starting
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <process_id> /F
```

### Dashboard Cannot Connect to RPis
- Verify RPis are powered on and running API servers
- Check network connectivity: `ping 192.168.1.101`
- Ensure firewall allows ports 8001-8003
- Check RPi API server logs

### No Data Appearing
- Verify file receiver is running on port 8000
- Check `C:/OctoBoard_Data/` directory permissions
- Review file receiver logs for upload errors
- Ensure RPis have correct Main PC IP configured

### Dashboard Shows Offline RPis
- Confirm RPi API servers are running
- Test RPi endpoints manually:
  ```powershell
  curl http://192.168.1.101:8001/status
  ```
- Check network switches and cables
- Verify IP addresses in dashboard match RPi configuration

## API Documentation

### File Receiver API

**POST /upload**
```json
{
  "file": "<binary file data>",
  "rpi_id": "rpi_1",
  "sample_id": "Sample_001",
  "pixel": "a"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "File uploaded successfully",
  "file_path": "C:/OctoBoard_Data/Sample_001/a/IV_20240101_120000.csv",
  "file_size": 12345
}
```

**GET /stats**
```json
{
  "files_received": 1250,
  "total_bytes": 15728640,
  "last_received": "2024-01-01T12:00:00"
}
```

## Development Notes

### Testing Without RPis
The system can be tested with mock RPis running in simulation mode:

```powershell
# Start mock RPi (simulate RPi 1)
cd ..\rpi_system
$env:OCTOBOARD_SIMULATION="True"
python api_server.py
```

### Customization

**Change data directory:**
Edit `dashboard.py` and `file_receiver.py`:
```python
DATA_ROOT = Path("D:/MyData")  # Change path
```

**Modify RPi IP addresses:**
Edit `dashboard.py`:
```python
RPIS = {
    "RPi 1": {"url": "http://192.168.2.101:8001", "id": "rpi_1"},
    # ...
}
```

**Adjust sweep interval:**
Edit `rpi_system/api_server.py`:
```python
IV_SWEEP_INTERVAL_HOURS = 2  # Change from 1 to 2 hours
```

## Performance

- **File Transfer Rate**: ~100 files/second
- **Dashboard Refresh**: ~1-2 seconds for 3 RPis
- **Storage**: ~10 KB per IV file, ~24 MB/day/sample (hourly sweeps)
- **Memory Usage**: Dashboard ~200 MB, File Receiver ~100 MB

## Safety Features

- File validation before storage
- Automatic directory creation
- Graceful handling of offline RPis
- Statistics tracking for monitoring
- No internet dependency (LAN only)

## Future Enhancements

- Database integration (SQLite/PostgreSQL)
- Email alerts for measurement completion
- Automatic data backup
- Multi-file IV curve comparison
- Export to Excel/PDF reports
- User authentication
- Measurement scheduling
- Data compression for long-term storage

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review logs in terminal windows
3. Verify network configuration
4. Test individual components separately

## License

Part of OctoBoard project - Solar cell MPPT testing system.

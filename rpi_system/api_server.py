"""
Raspberry Pi API Server
- Controls 96 channels (12 Octoboards × 8 channels)
- Handles 24 samples (each sample = 4 pixels = 4 channels)
- Hourly IV sweep generation
- Automatic file transfer to Main PC
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
import os
import threading
import time
import requests
import schedule
from datetime import datetime
from pathlib import Path

# Set simulation mode from environment
os.environ.setdefault('OCTOBOARD_SIMULATION', 'False')

from software.hardware.constants import (
    SIMULATION_MODE, 
    TOTAL_CHANNELS_PER_RPI, 
    SAMPLES_PER_RPI,
    PIXELS_PER_SAMPLE,
    IV_SWEEP_INTERVAL_HOURS,
    MAIN_PC_IP,
    MAIN_PC_PORT,
    FILE_TRANSFER_TIMEOUT
)
from software import get_hardware_classes

app = FastAPI(title="OctoBoard RPi API", version="2.0.0")

# Global state
board_manager = None
measurement_tasks = {}  # {sample_id: {pixel: {status, start_time, ...}}}
sample_configs = {}  # {sample_id: MeasurementConfig}
rpi_id = os.environ.get('RPI_ID', 'rpi_1')

# ==================== Data Models ====================

class MeasurementConfig(BaseModel):
    """Configuration for measuring a sample (4 pixels)."""
    sample_id: str
    start_channel: int  # Starting channel (0-95), will use this + 3 channels
    cell_area: float  # cm²
    current_limit: float  # mA
    start_voltage: float  # V
    stop_voltage: float  # V
    voltage_step: float  # V
    settle_time: float  # seconds
    sweep_interval_minutes: int = 60  # IV sweep interval in minutes (1-1000)
    measurement_type: str = "iv_sweep"  # or "mppt"
    mppt_iterations: Optional[int] = 100
    mppt_interval: Optional[float] = 0.01


class RPiStatus(BaseModel):
    """Status of this Raspberry Pi."""
    rpi_id: str
    simulation_mode: bool
    total_channels: int
    total_samples_capacity: int
    active_samples: int
    main_pc_connected: bool


# ==================== Hardware Initialization ====================

@app.on_event("startup")
async def startup_event():
    """Initialize hardware and start scheduler."""
    global board_manager
    
    print(f"[{rpi_id}] Starting up...")
    print(f"[{rpi_id}] Simulation Mode: {SIMULATION_MODE}")
    print(f"[{rpi_id}] Total Channels: {TOTAL_CHANNELS_PER_RPI}")
    print(f"[{rpi_id}] Sample Capacity: {SAMPLES_PER_RPI}")
    
    # Initialize hardware
    OBoardManager, _, _, _ = get_hardware_classes()
    i2c_num = int(os.environ.get('OCTOBOARD_I2C_BUS', '1'))
    board_manager = OBoardManager(i2c_num=i2c_num)
    
    print(f"[{rpi_id}] Initialized {len(board_manager.oboards)} boards")
    
    # Start scheduler thread for periodic IV sweeps
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print(f"[{rpi_id}] Scheduler started (per-sample intervals)")


def run_scheduler():
    """Run the scheduler in background thread - checks every minute."""
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


# ==================== API Endpoints ====================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "OctoBoard RPi API",
        "rpi_id": rpi_id,
        "version": "2.0.0",
        "simulation_mode": SIMULATION_MODE,
        "channels": TOTAL_CHANNELS_PER_RPI,
        "samples_capacity": SAMPLES_PER_RPI
    }


@app.get("/status", response_model=RPiStatus)
async def get_status():
    """Get current status."""
    # Test Main PC connection
    main_pc_connected = test_main_pc_connection()
    
    # Report actual available channels based on connected boards
    actual_channels = len(board_manager.oboards) * 8 if board_manager else 0
    actual_samples_capacity = actual_channels // 4
    
    return RPiStatus(
        rpi_id=rpi_id,
        simulation_mode=SIMULATION_MODE,
        total_channels=actual_channels,  # Actual available channels
        total_samples_capacity=actual_samples_capacity,  # Actual sample capacity
        active_samples=len(sample_configs),
        main_pc_connected=main_pc_connected
    )


@app.get("/channels")
async def list_channels():
    """List all 96 channels grouped by samples."""
    channels = []
    
    for sample_num in range(SAMPLES_PER_RPI):
        start_ch = sample_num * PIXELS_PER_SAMPLE
        sample_channels = []
        
        for pixel_idx, pixel_name in enumerate(['a', 'b', 'c', 'd']):
            ch_idx = start_ch + pixel_idx
            board_idx = ch_idx // 8
            local_ch = ch_idx % 8
            
            sample_channels.append({
                "pixel": pixel_name,
                "channel_index": ch_idx,
                "board_index": board_idx,
                "local_channel": local_ch,
                "status": "active" if is_channel_active(ch_idx) else "idle"
            })
        
        channels.append({
            "sample_slot": sample_num,
            "start_channel": start_ch,
            "channels": sample_channels,
            "assigned_sample": get_assigned_sample(start_ch)
        })
    
    return {"total_sample_slots": SAMPLES_PER_RPI, "samples": channels}


@app.post("/measurement/start")
async def start_measurement(config: MeasurementConfig, background_tasks: BackgroundTasks):
    """Start measuring a sample (4 pixels on 4 consecutive channels)."""
    
    # Check actual available channels based on connected boards
    actual_channels = len(board_manager.oboards) * 8 if board_manager else 0
    
    # Validate channel range
    if config.start_channel < 0 or config.start_channel + 3 >= actual_channels:
        raise HTTPException(400, f"Invalid start_channel. Only {actual_channels} channels available (must be 0-{actual_channels-4})")
    
    if config.start_channel % 4 != 0:
        raise HTTPException(400, "start_channel must be divisible by 4 (sample alignment)")
    
    # Check if already running
    if config.sample_id in sample_configs:
        raise HTTPException(400, f"Sample {config.sample_id} already running")
    
    # Store configuration
    sample_configs[config.sample_id] = config.dict()
    measurement_tasks[config.sample_id] = {
        pixel: {"status": "idle", "last_iv": None}
        for pixel in ['a', 'b', 'c', 'd']
    }
    
    print(f"[{rpi_id}] Started sample {config.sample_id} on channels {config.start_channel}-{config.start_channel+3}")
    print(f"[{rpi_id}] IV sweep interval: {config.sweep_interval_minutes} minutes")
    
    # Save Config.txt file
    save_config_file(config.sample_id, config)
    
    # Update Samples_Status.txt on Main PC
    update_samples_status_file()
    
    # Schedule periodic IV sweeps for this sample
    schedule.every(config.sweep_interval_minutes).minutes.do(
        perform_iv_sweep_for_sample, 
        sample_id=config.sample_id
    ).tag(config.sample_id)  # Tag allows us to cancel later
    
    # Perform initial IV sweep immediately
    background_tasks.add_task(perform_iv_sweep_for_sample, config.sample_id)
    
    return {
        "status": "started",
        "sample_id": config.sample_id,
        "channels": list(range(config.start_channel, config.start_channel + 4)),
        "sweep_interval_minutes": config.sweep_interval_minutes,
        "message": f"Sample measurement started with {config.sweep_interval_minutes} min interval"
    }


@app.post("/measurement/stop/{sample_id}")
async def stop_measurement(sample_id: str):
    """Stop measuring a sample and cancel its scheduled sweeps."""
    if sample_id not in sample_configs:
        raise HTTPException(404, f"Sample {sample_id} not found")
    
    # Cancel scheduled jobs for this sample
    schedule.clear(sample_id)
    
    del sample_configs[sample_id]
    del measurement_tasks[sample_id]
    
    print(f"[{rpi_id}] Stopped sample {sample_id}")
    
    # Update Samples_Status.txt on Main PC
    update_samples_status_file()
    
    return {
        "status": "stopped",
        "sample_id": sample_id
    }


@app.get("/measurement/{sample_id}")
async def get_measurement_status(sample_id: str):
    """Get status of a sample measurement."""
    if sample_id not in measurement_tasks:
        raise HTTPException(404, f"Sample {sample_id} not found")
    
    return {
        "sample_id": sample_id,
        "pixels": measurement_tasks[sample_id],
        "config": sample_configs.get(sample_id)
    }


# ==================== Measurement Functions ====================

def perform_iv_sweep_for_sample(sample_id: str):
    """Perform IV sweep for all 4 pixels of a sample."""
    if sample_id not in sample_configs:
        return
    
    config_dict = sample_configs[sample_id]
    config = MeasurementConfig(**config_dict)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    for pixel_idx, pixel_name in enumerate(['a', 'b', 'c', 'd']):
        try:
            ch_idx = config.start_channel + pixel_idx
            board_idx = ch_idx // 8
            local_ch = ch_idx % 8
            
            if board_idx >= len(board_manager.oboards):
                print(f"[{rpi_id}] ERROR: Board {board_idx} not available")
                continue
            
            channel = board_manager.oboards[board_idx].channel[local_ch]
            
            # Update status
            measurement_tasks[sample_id][pixel_name]["status"] = "measuring"
            
            print(f"[{rpi_id}] IV sweep: {sample_id}/{pixel_name} on channel {ch_idx}")
            
            # Perform IV sweep
            import numpy as np
            data = []
            
            for voltage in np.arange(config.start_voltage, 
                                    config.stop_voltage + config.voltage_step, 
                                    config.voltage_step):
                channel.set_voltage(voltage)
                time.sleep(config.settle_time)
                
                v = channel.read_voltage()
                i = channel.read_current()
                
                # Check current limit
                if abs(i * 1000) > config.current_limit:
                    print(f"[{rpi_id}] Current limit exceeded: {sample_id}/{pixel_name}")
                    break
                
                data.append({
                    "timestamp": datetime.now().isoformat(),
                    "voltage": v,
                    "current": i,
                    "power": v * i
                })
            
            channel.set_voltage(0)  # Safety
            
            # Save IV data locally
            local_file = save_iv_data_locally(sample_id, pixel_name, timestamp, data)
            
            # Transfer to Main PC
            transfer_file_to_main_pc(sample_id, pixel_name, local_file)
            
            # Update status
            measurement_tasks[sample_id][pixel_name]["status"] = "idle"
            measurement_tasks[sample_id][pixel_name]["last_iv"] = timestamp
            
        except Exception as e:
            print(f"[{rpi_id}] ERROR in IV sweep {sample_id}/{pixel_name}: {e}")
            measurement_tasks[sample_id][pixel_name]["status"] = "error"


def update_samples_status_file():
    """Create/update Samples_Status.txt on Main PC showing all active samples."""
    try:
        # Create status content
        status_content = f"=== OctoBoard Samples Status ===\n"
        status_content += f"RPi ID: {rpi_id}\n"
        status_content += f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        status_content += f"Active Samples: {len(sample_configs)}/{SAMPLES_PER_RPI}\n"
        status_content += f"\n"
        
        if sample_configs:
            status_content += f"{'Sample ID':<20} {'Channels':<15} {'Interval':<15} {'Status'}\n"
            status_content += f"{'-'*70}\n"
            
            for sample_id, config_dict in sample_configs.items():
                config = MeasurementConfig(**config_dict)
                channels = f"{config.start_channel}-{config.start_channel+3}"
                interval = f"{config.sweep_interval_minutes} min"
                status = "Running"
                status_content += f"{sample_id:<20} {channels:<15} {interval:<15} {status}\n"
        else:
            status_content += "No active samples\n"
        
        # Save locally
        local_path = Path(f"/tmp/octoboard_{rpi_id}/Samples_Status.txt")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        with open(local_path, 'w') as f:
            f.write(status_content)
        
        # Transfer to Main PC root folder
        main_pc_url = f"http://{MAIN_PC_IP}:{MAIN_PC_PORT}/upload"
        print(f"[{rpi_id}] Transferring Samples_Status.txt to {main_pc_url}...")
        with open(local_path, 'rb') as f:
            files = {'file': (f'{rpi_id}_Samples_Status.txt', f, 'text/plain')}
            data = {
                'rpi_id': rpi_id,
                'sample_id': '',  # Status file is at root level
                'pixel': ''
            }
            response = requests.post(main_pc_url, files=files, data=data, timeout=FILE_TRANSFER_TIMEOUT)
            print(f"[{rpi_id}] Samples_Status.txt transfer response: {response.status_code}")
            if response.status_code == 200:
                print(f"[{rpi_id}] Updated Samples_Status.txt on Main PC")
            else:
                print(f"[{rpi_id}] Samples_Status.txt transfer failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[{rpi_id}] Failed to update Samples_Status.txt: {e}")
        import traceback
        traceback.print_exc()


def save_config_file(sample_id: str, config: MeasurementConfig):
    """Save Config.txt in the sample folder."""
    local_dir = Path(f"/tmp/octoboard_{rpi_id}/IV/{sample_id}")
    local_dir.mkdir(parents=True, exist_ok=True)
    
    config_path = local_dir / "Config.txt"
    
    with open(config_path, 'w') as f:
        f.write(f"Sample ID: {sample_id}\n")
        f.write(f"RPI ID: {rpi_id}\n")
        f.write(f"Start Channel: {config.start_channel}\n")
        f.write(f"Channels Used: {config.start_channel} to {config.start_channel + 3}\n")
        f.write(f"Cell Area: {config.cell_area} cm²\n")
        f.write(f"Current Limit: {config.current_limit} mA\n")
        f.write(f"Start Voltage: {config.start_voltage} V\n")
        f.write(f"Stop Voltage: {config.stop_voltage} V\n")
        f.write(f"Voltage Step: {config.voltage_step} V\n")
        f.write(f"Settle Time: {config.settle_time} s\n")
        f.write(f"Measurement Type: {config.measurement_type}\n")
        f.write(f"IV Sweep Interval: {config.sweep_interval_minutes} minute(s)\n")
        f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"[{rpi_id}] Created Config.txt for {sample_id}")
    
    # Transfer to Main PC
    try:
        main_pc_url = f"http://{MAIN_PC_IP}:{MAIN_PC_PORT}/upload"
        print(f"[{rpi_id}] Transferring Config.txt to {main_pc_url}...")
        with open(config_path, 'rb') as f:
            files = {'file': (config_path.name, f, 'text/plain')}
            data = {
                'rpi_id': rpi_id,
                'sample_id': sample_id,
                'pixel': ''  # Config is at sample level, not pixel level
            }
            response = requests.post(main_pc_url, files=files, data=data, timeout=FILE_TRANSFER_TIMEOUT)
            print(f"[{rpi_id}] Config.txt transfer response: {response.status_code}")
            if response.status_code == 200:
                print(f"[{rpi_id}] Transferred Config.txt → Main PC")
            else:
                print(f"[{rpi_id}] Config.txt transfer failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[{rpi_id}] Config.txt transfer error: {e}")
        import traceback
        traceback.print_exc()


def save_iv_data_locally(sample_id: str, pixel: str, timestamp: str, data: List[Dict]) -> Path:
    """Save IV data to local file."""
    import pandas as pd
    
    # Create directory structure
    local_dir = Path(f"/tmp/octoboard_{rpi_id}/IV/{sample_id}/{pixel}")
    local_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    filename = f"IV_{timestamp}.csv"
    filepath = local_dir / filename
    
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)
    
    print(f"[{rpi_id}] Saved: {filepath}")
    return filepath


def transfer_file_to_main_pc(sample_id: str, pixel: str, filepath: Path):
    """Transfer IV file to Main PC via HTTP POST."""
    try:
        main_pc_url = f"http://{MAIN_PC_IP}:{MAIN_PC_PORT}/upload"
        
        with open(filepath, 'rb') as f:
            files = {'file': (filepath.name, f, 'text/csv')}
            data = {
                'rpi_id': rpi_id,
                'sample_id': sample_id,
                'pixel': pixel
            }
            
            response = requests.post(
                main_pc_url,
                files=files,
                data=data,
                timeout=FILE_TRANSFER_TIMEOUT
            )
            
            if response.status_code == 200:
                print(f"[{rpi_id}] Transferred: {sample_id}/{pixel} → Main PC")
            else:
                print(f"[{rpi_id}] Transfer failed: {response.status_code}")
                
    except Exception as e:
        print(f"[{rpi_id}] Transfer error: {e}")


def test_main_pc_connection() -> bool:
    """Test if Main PC is reachable."""
    try:
        response = requests.get(
            f"http://{MAIN_PC_IP}:{MAIN_PC_PORT}/ping",
            timeout=2
        )
        return response.status_code == 200
    except:
        return False


def is_channel_active(ch_idx: int) -> bool:
    """Check if a channel is currently assigned to a sample."""
    for sample_id, config in sample_configs.items():
        start_ch = config['start_channel']
        if start_ch <= ch_idx < start_ch + 4:
            return True
    return False


def get_assigned_sample(start_ch: int) -> Optional[str]:
    """Get sample ID assigned to a channel slot."""
    for sample_id, config in sample_configs.items():
        if config['start_channel'] == start_ch:
            return sample_id
    return None


# ==================== Server Launcher ====================

if __name__ == "__main__":
    port = int(os.environ.get('API_PORT', '8001'))
    uvicorn.run(app, host="0.0.0.0", port=port)

"""
FastAPI server for Raspberry Pi - receives commands from Main PC.
Runs alongside the measurement system to provide remote control.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import threading
import os
from datetime import datetime

# Import hardware after setting simulation mode
from .hardware.constants import SIMULATION_MODE

if SIMULATION_MODE:
    print("[API] Running in SIMULATION mode")

from . import get_hardware_classes
OBoardManager, _, _, _ = get_hardware_classes()

app = FastAPI(title="OctoBoard RPi API", version="1.0.0")

# Global state
board_manager = None
measurement_tasks = {}  # {channel_id: task_info}
current_config = {}


# ==================== Data Models ====================
class MeasurementConfig(BaseModel):
    """Configuration for a measurement on a specific channel."""
    sample_id: str
    channel_index: int  # 0-7
    cell_area: float  # cm²
    current_limit: float  # mA
    start_voltage: float  # V
    stop_voltage: float  # V
    voltage_step: float  # V
    settle_time: float  # seconds
    pixels: List[str] = ["a", "b", "c", "d"]  # Default 4 pixels
    measurement_type: str = "iv_sweep"  # or "mppt"
    mppt_iterations: Optional[int] = 100
    mppt_interval: Optional[float] = 0.01


class RPiStatus(BaseModel):
    """Status of the Raspberry Pi."""
    rpi_id: str
    simulation_mode: bool
    num_boards: int
    total_channels: int
    active_measurements: int
    uptime: float


# ==================== API Endpoints ====================

@app.on_event("startup")
async def startup_event():
    """Initialize hardware on startup."""
    global board_manager
    i2c_num = int(os.environ.get('OCTOBOARD_I2C_BUS', '1'))
    board_manager = OBoardManager(i2c_num=i2c_num)
    print(f"[API] Initialized {len(board_manager.oboards)} boards on I2C bus {i2c_num}")


@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "name": "OctoBoard RPi API",
        "version": "1.0.0",
        "simulation_mode": SIMULATION_MODE,
        "status": "running"
    }


@app.get("/status", response_model=RPiStatus)
async def get_status():
    """Get current status of this Raspberry Pi."""
    if not board_manager:
        raise HTTPException(status_code=500, detail="Board manager not initialized")
    
    return RPiStatus(
        rpi_id=os.environ.get('RPI_ID', 'rpi_1'),
        simulation_mode=SIMULATION_MODE,
        num_boards=len(board_manager.oboards),
        total_channels=len(board_manager.oboards) * 8,
        active_measurements=len(measurement_tasks),
        uptime=0.0  # TODO: calculate actual uptime
    )


@app.get("/channels")
async def list_channels():
    """List all available channels with their current status."""
    if not board_manager:
        raise HTTPException(status_code=500, detail="Board manager not initialized")
    
    channels = []
    for board_idx, board in enumerate(board_manager.oboards):
        for ch_idx in range(8):
            channel = board.channel[ch_idx]
            channel_id = f"board{board_idx}_ch{ch_idx}"
            channels.append({
                "channel_id": channel_id,
                "board_index": board_idx,
                "channel_index": ch_idx,
                "full_id": channel.id,
                "status": "active" if channel_id in measurement_tasks else "idle",
                "last_voltage": channel.last_v if hasattr(channel, 'last_v') else 0.0
            })
    
    return {"channels": channels}


@app.post("/measurement/start")
async def start_measurement(config: MeasurementConfig, background_tasks: BackgroundTasks):
    """Start a measurement on a specific channel."""
    if not board_manager:
        raise HTTPException(status_code=500, detail="Board manager not initialized")
    
    # Validate channel exists
    board_idx = config.channel_index // 8
    ch_idx = config.channel_index % 8
    
    if board_idx >= len(board_manager.oboards):
        raise HTTPException(status_code=400, detail=f"Board {board_idx} not found")
    
    channel = board_manager.oboards[board_idx].channel[ch_idx]
    channel_id = f"board{board_idx}_ch{ch_idx}"
    
    if channel_id in measurement_tasks:
        raise HTTPException(status_code=400, detail=f"Channel {channel_id} already running")
    
    # Store configuration
    current_config[channel_id] = config.dict()
    measurement_tasks[channel_id] = {
        "status": "running",
        "start_time": datetime.now().isoformat(),
        "config": config.dict()
    }
    
    # Start measurement in background
    if config.measurement_type == "iv_sweep":
        background_tasks.add_task(
            run_iv_sweep_with_pixels,
            channel, config, channel_id
        )
    else:  # mppt
        background_tasks.add_task(
            run_mppt_with_pixels,
            channel, config, channel_id
        )
    
    return {
        "status": "started",
        "channel_id": channel_id,
        "sample_id": config.sample_id,
        "message": f"Measurement started on channel {config.channel_index}"
    }


@app.post("/measurement/stop/{channel_index}")
async def stop_measurement(channel_index: int):
    """Stop a measurement on a specific channel."""
    board_idx = channel_index // 8
    ch_idx = channel_index % 8
    channel_id = f"board{board_idx}_ch{ch_idx}"
    
    if channel_id not in measurement_tasks:
        raise HTTPException(status_code=400, detail=f"No active measurement on channel {channel_index}")
    
    # Mark as stopped (the background task should check this)
    measurement_tasks[channel_id]["status"] = "stopped"
    
    return {
        "status": "stopped",
        "channel_id": channel_id,
        "message": f"Measurement stopped on channel {channel_index}"
    }


@app.get("/measurement/{channel_index}")
async def get_measurement_status(channel_index: int):
    """Get status of measurement on a specific channel."""
    board_idx = channel_index // 8
    ch_idx = channel_index % 8
    channel_id = f"board{board_idx}_ch{ch_idx}"
    
    if channel_id not in measurement_tasks:
        return {"status": "idle", "channel_id": channel_id}
    
    return measurement_tasks[channel_id]


# ==================== Background Tasks ====================

def run_iv_sweep_with_pixels(channel, config: MeasurementConfig, channel_id: str):
    """Run IV sweep for all 4 pixels of a sample."""
    try:
        import numpy as np
        
        for pixel in config.pixels:
            # Check if stopped
            if measurement_tasks.get(channel_id, {}).get("status") == "stopped":
                break
            
            print(f"[{channel_id}] Running IV sweep for sample {config.sample_id} pixel {pixel}")
            
            # Update channel configuration
            # Note: This assumes channel can cycle through pixels
            # You may need to implement pixel switching logic in your hardware
            
            # Perform IV sweep with custom parameters
            data = []
            for voltage in np.arange(config.start_voltage, 
                                    config.stop_voltage + config.voltage_step, 
                                    config.voltage_step):
                channel.set_voltage(voltage)
                import time
                time.sleep(config.settle_time)
                
                v = channel.read_voltage()
                i = channel.read_current()
                
                # Check current limit
                if abs(i * 1000) > config.current_limit:  # Convert A to mA
                    print(f"[{channel_id}] Current limit exceeded for pixel {pixel}")
                    break
                
                data.append({
                    "timestamp": datetime.now().isoformat(),
                    "voltage": v,
                    "current": i,
                    "pixel": pixel,
                    "sample_id": config.sample_id
                })
            
            # Send data to Main PC (implement this next)
            send_data_to_main_pc(config.sample_id, pixel, data)
            
        measurement_tasks[channel_id]["status"] = "completed"
        measurement_tasks[channel_id]["end_time"] = datetime.now().isoformat()
        
    except Exception as e:
        print(f"[{channel_id}] Error: {e}")
        measurement_tasks[channel_id]["status"] = "error"
        measurement_tasks[channel_id]["error"] = str(e)
    finally:
        channel.set_voltage(0)  # Safety: set to 0V


def run_mppt_with_pixels(channel, config: MeasurementConfig, channel_id: str):
    """Run MPPT tracking for all 4 pixels of a sample."""
    try:
        for pixel in config.pixels:
            if measurement_tasks.get(channel_id, {}).get("status") == "stopped":
                break
            
            print(f"[{channel_id}] Running MPPT for sample {config.sample_id} pixel {pixel}")
            
            # Run MPPT for this pixel
            channel.mpp_track(
                iterations=config.mppt_iterations or 100,
                interval=config.mppt_interval or 0.01
            )
            
        measurement_tasks[channel_id]["status"] = "completed"
        
    except Exception as e:
        print(f"[{channel_id}] Error: {e}")
        measurement_tasks[channel_id]["status"] = "error"
        measurement_tasks[channel_id]["error"] = str(e)


def send_data_to_main_pc(sample_id: str, pixel: str, data: List[dict]):
    """Send measurement data to Main PC."""
    main_pc_url = os.environ.get('MAIN_PC_URL', 'http://192.168.1.100:8000')
    
    try:
        import requests
        response = requests.post(
            f"{main_pc_url}/data/upload",
            json={
                "sample_id": sample_id,
                "pixel": pixel,
                "data": data
            },
            timeout=10
        )
        print(f"[API] Data sent to Main PC: {response.status_code}")
    except Exception as e:
        print(f"[API] Failed to send data to Main PC: {e}")
        # TODO: Queue for retry


# ==================== Server Launcher ====================

def run_api_server(host="0.0.0.0", port=8001):
    """Run the FastAPI server."""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_api_server()

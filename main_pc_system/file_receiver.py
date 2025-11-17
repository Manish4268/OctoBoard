"""
Main PC File Receiver API
Receives IV data files from Raspberry Pis and stores them in organized structure.
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from pathlib import Path
from datetime import datetime
import shutil

app = FastAPI(title="OctoBoard Main PC File Receiver", version="1.0.0")

# Configuration
DATA_ROOT = Path("C:/Users/ManishJadhav/SynologyDrive/Rayleigh/Outdoor Data")
DATA_ROOT.mkdir(parents=True, exist_ok=True)

# Statistics
stats = {
    "files_received": 0,
    "total_bytes": 0,
    "last_received": None
}

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "OctoBoard Main PC File Receiver",
        "version": "1.0.0",
        "data_root": str(DATA_ROOT),
        "stats": stats
    }


@app.get("/ping")
async def ping():
    """Health check endpoint for RPis."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    rpi_id: str = Form(...),
    sample_id: str = Form(""),  # Optional, empty for status files
    pixel: str = Form("")  # Optional, empty for config and status files
):
    """
    Receive IV data file from Raspberry Pi.
    
    File will be stored in:
    - Config.txt: DATA_ROOT/sample_id/Config.txt
    - IV data: DATA_ROOT/sample_id/pixel/filename.csv
    """
    try:
        print(f"[DEBUG] Receiving file: {file.filename} from {rpi_id} for {sample_id}/{pixel}")
        print(f"[DEBUG] DATA_ROOT: {DATA_ROOT}")
        
        # Handle status files at root level
        if sample_id == '' and 'Status' in file.filename:
            # Status file goes in DATA_ROOT
            file_path = DATA_ROOT / file.filename
            print(f"[DEBUG] Status file path: {file_path}")
        else:
            # Create sample directory
            sample_dir = DATA_ROOT / sample_id
            sample_dir.mkdir(parents=True, exist_ok=True)
            print(f"[DEBUG] Created sample_dir: {sample_dir}")
            
            # Determine file path based on whether it's Config.txt or IV data
            if pixel == '' or file.filename == 'Config.txt':
                # Config file goes in sample root directory
                file_path = sample_dir / file.filename
                print(f"[DEBUG] Config file path: {file_path}")
            else:
                # Validate pixel for IV data files
                if pixel not in ['a', 'b', 'c', 'd']:
                    raise HTTPException(400, f"Invalid pixel: {pixel}")
                
                # IV data goes in pixel subdirectory
                pixel_dir = sample_dir / pixel
                pixel_dir.mkdir(parents=True, exist_ok=True)
                file_path = pixel_dir / file.filename
                print(f"[DEBUG] IV file path: {file_path}")
        
        with open(file_path, 'wb') as f:
            content = await file.read()
            f.write(content)
            file_size = len(content)
        
        print(f"[DEBUG] Saved {file_size} bytes to {file_path}")
        
        # Update statistics
        stats["files_received"] += 1
        stats["total_bytes"] += file_size
        stats["last_received"] = datetime.now().isoformat()
        
        print(f"[RECEIVED] {rpi_id} → {sample_id}/{pixel}/{file.filename} ({file_size} bytes)")
        
        return {
            "status": "success",
            "rpi_id": rpi_id,
            "sample_id": sample_id,
            "pixel": pixel,
            "filename": file.filename,
            "size_bytes": file_size,
            "path": str(file_path)
        }
        
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        raise HTTPException(500, f"Upload failed: {str(e)}")


@app.get("/stats")
async def get_stats():
    """Get file receiver statistics."""
    return stats


@app.get("/samples")
async def list_samples():
    """List all samples in data directory."""
    samples = []
    
    if DATA_ROOT.exists():
        for sample_dir in sorted(DATA_ROOT.iterdir()):
            if sample_dir.is_dir():
                pixels = {}
                for pixel in ['a', 'b', 'c', 'd']:
                    pixel_dir = sample_dir / pixel
                    if pixel_dir.exists():
                        files = list(pixel_dir.glob("*.csv"))
                        pixels[pixel] = {
                            "file_count": len(files),
                            "latest_file": files[-1].name if files else None
                        }
                
                samples.append({
                    "sample_id": sample_dir.name,
                    "pixels": pixels
                })
    
    return {"total_samples": len(samples), "samples": samples}


@app.get("/sample/{sample_id}")
async def get_sample_files(sample_id: str):
    """Get all files for a specific sample."""
    sample_dir = DATA_ROOT / sample_id
    
    if not sample_dir.exists():
        raise HTTPException(404, f"Sample {sample_id} not found")
    
    files = {}
    for pixel in ['a', 'b', 'c', 'd']:
        pixel_dir = sample_dir / pixel
        if pixel_dir.exists():
            files[pixel] = [f.name for f in sorted(pixel_dir.glob("*.csv"))]
    
    return {
        "sample_id": sample_id,
        "path": str(sample_dir),
        "files": files
    }


if __name__ == "__main__":
    print(f"Starting Main PC File Receiver...")
    print(f"Data will be stored in: {DATA_ROOT}")
    print(f"Listening on port 8000...")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

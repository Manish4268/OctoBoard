# Git Push Instructions for OctoBoard v2.0

## Before You Push - Checklist

### ✅ Files to INCLUDE (Production Code):
- `rpi_system/` - All RPi code
  - `api_server.py` - Main API server
  - `start_rpi.sh` - Startup script
  - `requirements.txt` - Dependencies
  - `software/` - Hardware control code
- `main_pc_system/` - All Main PC code
  - `dashboard.py` - Streamlit dashboard
  - `file_receiver.py` - File receiver API
  - `requirements.txt` - Dependencies
- `docs/` - Documentation
- `hardware/` - PCB designs
- `examples/` - Example code
- `PRODUCTION_DEPLOYMENT.md` - Production guide
- `RPi_BEGINNER_GUIDE.md` - Beginner's guide
- `readme.md` - Main README
- `.gitignore` - Git ignore file

### ❌ Files to EXCLUDE (Already in .gitignore):
- `venv/` - Virtual environments
- `__pycache__/` - Python cache
- `*.pyc` - Compiled Python
- `data/` - Measurement data
- `IV/` - IV sweep data
- `tmp/` - Temporary files
- `.vscode/` - IDE settings

---

## Step-by-Step Git Push Commands

### 1. Check Current Status
```powershell
cd C:\Users\ManishJadhav\OctoBoard
git status
```

### 2. Add All Production Files
```powershell
# Add all files (respects .gitignore)
git add .

# Review what will be committed
git status
```

### 3. Commit Changes
```powershell
git commit -m "v2.0: Production-ready system with configurable intervals and auto-detection

- Added configurable IV sweep intervals (1-1000 minutes per sample)
- Implemented persistent state management with status files
- Added automatic hardware detection (1-12 Octoboards)
- Optimized dashboard with pagination for 288+ channels
- Created production deployment guides
- Added beginner's guide for Raspberry Pi setup
- Fixed channel assignment to prevent conflicts
- Updated file receiver to handle config and status files
- Added systemd service for auto-start
- Improved performance with caching and form optimization"
```

### 4. Push to GitHub
```powershell
# Push to main branch
git push origin main

# If this is the first push or branch doesn't exist
git push -u origin main
```

---

## Alternative: Stage Files Selectively

If you want to review each file before committing:

```powershell
# Add specific directories
git add rpi_system/
git add main_pc_system/
git add docs/
git add hardware/
git add examples/

# Add documentation files
git add readme.md
git add PRODUCTION_DEPLOYMENT.md
git add RPi_BEGINNER_GUIDE.md
git add .gitignore

# Check what's staged
git status

# Commit
git commit -m "v2.0: Production-ready release"

# Push
git push origin main
```

---

## What .gitignore Excludes

The `.gitignore` file prevents these from being pushed:
- Virtual environments (`venv/`, `env/`)
- Python cache (`__pycache__/`, `*.pyc`)
- IDE files (`.vscode/`, `.idea/`)
- Data files (`data/`, `IV/`, `*.csv`)
- Temporary files (`tmp/`, `*.tmp`)
- System files (`.DS_Store`, `Thumbs.db`)
- Logs (`*.log`)

---

## Verify Before Pushing

```powershell
# See what will be committed (excluding ignored files)
git diff --cached

# List all files that will be pushed
git ls-files
```

---

## After Pushing

### Verify on GitHub
1. Go to https://github.com/Manish4268/OctoBoard
2. Check that all files are present
3. Verify README displays correctly
4. Check documentation files are readable

### Tag the Release
```powershell
# Create a version tag
git tag -a v2.0.0 -m "Production-ready v2.0 release"
git push origin v2.0.0
```

---

## Quick Reference

### Full Push (One Command)
```powershell
cd C:\Users\ManishJadhav\OctoBoard
git add .
git commit -m "v2.0: Production-ready system"
git push origin main
```

### Check Remote
```powershell
git remote -v
```

### Force Push (Use with caution!)
```powershell
# Only if you need to overwrite remote
git push -f origin main
```

---

## Important Notes

1. **Data Safety**: The `.gitignore` prevents actual measurement data from being pushed
2. **Venv Excluded**: Virtual environments are not pushed - users will create their own
3. **Clean Code**: Only production-ready code will be pushed
4. **Documentation**: All guides and READMEs are included

---

## Files Structure That Will Be Pushed

```
OctoBoard/
├── .gitignore
├── readme.md
├── PRODUCTION_DEPLOYMENT.md
├── RPi_BEGINNER_GUIDE.md
├── docs/
│   ├── images/
│   └── videos/
├── hardware/
│   ├── Measurement Chuck Housing CAD Design/
│   ├── Measurement Chuck PCB Design/
│   └── Octoboard PCB Design/
├── examples/
│   ├── examples.md
│   └── GUI_Marburg/
├── rpi_system/
│   ├── api_server.py
│   ├── start_rpi.sh
│   ├── requirements.txt
│   └── software/
│       └── hardware/
│           ├── __init__.py
│           ├── channel.py
│           ├── constants.py
│           ├── i2c.py
│           ├── manager.py
│           ├── oboard.py
│           └── sdac.py
└── main_pc_system/
    ├── dashboard.py
    ├── file_receiver.py
    └── requirements.txt
```

**✅ Ready to push! All production code, no clutter!**

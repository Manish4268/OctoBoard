#!/bin/bash
# OctoBoard RPi Startup Script
# Use this to start the API server on Raspberry Pi

# Configuration - EDIT THESE VALUES
export RPI_ID="${RPI_ID:-rpi_1}"                    # RPi identifier (rpi_1, rpi_2, or rpi_3)
export MAIN_PC_IP="${MAIN_PC_IP:-192.168.2.1}"      # Main PC IP address (direct Ethernet connection)
export API_PORT="${API_PORT:-8001}"                 # API port (8001 for RPi1, 8002 for RPi2, 8003 for RPi3)
export OCTOBOARD_SIMULATION="${OCTOBOARD_SIMULATION:-False}"  # False for real hardware, True for testing
export OCTOBOARD_I2C_BUS="${OCTOBOARD_I2C_BUS:-1}"  # I2C bus number (usually 1)

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting OctoBoard RPi API Server${NC}"
echo "========================================="
echo -e "RPi ID: ${YELLOW}$RPI_ID${NC}"
echo -e "Main PC IP: ${YELLOW}$MAIN_PC_IP${NC}"
echo -e "API Port: ${YELLOW}$API_PORT${NC}"
echo -e "Simulation Mode: ${YELLOW}$OCTOBOARD_SIMULATION${NC}"
echo -e "I2C Bus: ${YELLOW}$OCTOBOARD_I2C_BUS${NC}"
echo "========================================="

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check I2C if not in simulation mode
if [ "$OCTOBOARD_SIMULATION" = "False" ]; then
    echo -e "${YELLOW}🔍 Checking I2C...${NC}"
    
    if [ ! -e /dev/i2c-1 ]; then
        echo -e "${RED}❌ I2C not enabled!${NC}"
        echo "Run: sudo raspi-config → Interface Options → I2C → Enable"
        exit 1
    fi
    
    echo -e "${GREEN}✅ I2C enabled${NC}"
    
    # Scan I2C devices
    if command -v i2cdetect &> /dev/null; then
        echo -e "${YELLOW}📡 Scanning I2C devices...${NC}"
        sudo i2cdetect -y 1
    fi
fi

# Check if Main PC is reachable
echo -e "${YELLOW}🌐 Testing connection to Main PC...${NC}"
if ping -c 1 -W 2 $MAIN_PC_IP &> /dev/null; then
    echo -e "${GREEN}✅ Main PC reachable${NC}"
else
    echo -e "${RED}⚠️  Warning: Cannot reach Main PC at $MAIN_PC_IP${NC}"
    echo "Server will start anyway, but file transfers may fail."
fi

# Start the server
echo -e "${GREEN}🚀 Starting API server...${NC}"
python api_server.py

# If server exits, show message
echo -e "${RED}❌ Server stopped${NC}"

"""
Main PC Control Dashboard - Streamlit Application
Manages 3 Raspberry Pis (288 channels total, 72 samples)
"""

import streamlit as st
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import time
import plotly.express as px
import plotly.graph_objects as go

# Configuration
DATA_ROOT = Path("C:/Users/ManishJadhav/SynologyDrive/Rayleigh/Outdoor Data")
DATA_ROOT.mkdir(parents=True, exist_ok=True)

# RPi Configuration
# For production with real hardware - direct Ethernet connection
RPIS = {
    "RPi 1": {"url": "http://192.168.2.10:8001", "id": "rpi_1"},
    "RPi 2": {"url": "http://192.168.2.11:8002", "id": "rpi_2"},  # Add when available
    # "RPi 3": {"url": "http://192.168.2.12:8003", "id": "rpi_3"},  # Add when available
}

FILE_RECEIVER_URL = "http://localhost:8000"

# Configure Streamlit page
st.set_page_config(
    page_title="OctoBoard Control",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== Helper Functions ====================

@st.cache_data(ttl=10)  # Cache for 10 seconds
def read_all_status_files():
    """Read all RPi status files to find which channels are in use."""
    used_channels = {}  # {rpi_id: [list of used channels]}
    
    for rpi_name, rpi_info in RPIS.items():
        rpi_id = rpi_info["id"]
        status_file = DATA_ROOT / f"{rpi_id}_Samples_Status.txt"
        used_channels[rpi_id] = []
        
        if status_file.exists():
            try:
                with open(status_file, 'r') as f:
                    content = f.read()
                    print(f"[DEBUG] Reading {rpi_id} status file...")
                    # Parse the status file to extract channel ranges
                    # Format: "Sample ID            Channels        Interval        Status"
                    #         "1111                 0-3             60 min          Running"
                    in_data_section = False
                    for line in content.split('\n'):
                        line = line.strip()
                        
                        # Skip until we pass the header line with dashes
                        if line.startswith('-'):
                            in_data_section = True
                            continue
                        
                        # Parse data lines (after the dashes)
                        if in_data_section and line and not line.startswith('No active'):
                            parts = line.split()
                            if len(parts) >= 2:
                                # Second column should be channel range like "0-3"
                                channel_str = parts[1]
                                if '-' in channel_str:
                                    try:
                                        start, end = map(int, channel_str.split('-'))
                                        used_channels[rpi_id].extend(range(start, end+1))
                                        print(f"[DEBUG] Found channels {start}-{end} in use")
                                    except:
                                        pass
            except Exception as e:
                print(f"[DEBUG] Error reading status file for {rpi_id}: {e}")
    
    print(f"[DEBUG] Used channels: {used_channels}")
    return used_channels


def get_next_available_channel(rpi_id, used_channels):
    """Find the next available set of 4 consecutive channels on an RPi."""
    used = set(used_channels.get(rpi_id, []))
    
    # Check every possible starting channel (0, 4, 8, 12, ...)
    for start_channel in range(0, 96, 4):  # 96 channels total per RPi
        channels_needed = [start_channel, start_channel+1, start_channel+2, start_channel+3]
        if not any(ch in used for ch in channels_needed):
            return start_channel
    
    return None  # No available channels


@st.cache_data(ttl=5)  # Cache for 5 seconds
def get_rpi_status(rpi_url):
    """Get status from RPi."""
    try:
        response = requests.get(f"{rpi_url}/status", timeout=10)
        result = response.json() if response.status_code == 200 else None
        return result
    except Exception as e:
        return None


@st.cache_data(ttl=5)  # Cache for 5 seconds
def get_rpi_channels(rpi_url):
    """Get channels from RPi."""
    try:
        response = requests.get(f"{rpi_url}/channels", timeout=10)
        return response.json() if response.status_code == 200 else None
    except:
        return None


def start_measurement(rpi_url, config):
    """Start measurement on RPi."""
    try:
        response = requests.post(f"{rpi_url}/measurement/start", json=config, timeout=30)
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, {"error": str(e)}


def stop_measurement(rpi_url, sample_id):
    """Stop measurement on RPi."""
    try:
        response = requests.post(f"{rpi_url}/measurement/stop/{sample_id}", timeout=5)
        return response.status_code == 200
    except:
        return False


@st.cache_data(ttl=5)  # Cache for 5 seconds
def get_file_receiver_stats():
    """Get statistics from file receiver."""
    try:
        response = requests.get(f"{FILE_RECEIVER_URL}/stats", timeout=2)
        return response.json() if response.status_code == 200 else None
    except:
        return None


# ==================== Streamlit UI ====================

# Initialize session state
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()
    st.session_state.rpi_statuses = None
    st.session_state.receiver_stats = None
    st.session_state.need_refresh = True

# Title and Header
col1, col2, col3 = st.columns([2, 3, 2])
with col2:
    st.title("⚡ OctoBoard Control Center")

st.markdown("---")

# ==================== Sidebar: System Status ====================

with st.sidebar:
    st.header("🖥️ System Status")
    
    # Manual refresh button
    if st.button("🔄 Refresh Status", key="refresh_status"):
        st.session_state.need_refresh = True
        st.session_state.last_refresh = time.time()
        st.cache_data.clear()
    
    st.caption(f"Last refresh: {datetime.fromtimestamp(st.session_state.last_refresh).strftime('%H:%M:%S')}")
    
    # Only fetch status if needed (first load or manual refresh)
    if st.session_state.need_refresh:
        st.session_state.receiver_stats = get_file_receiver_stats()
        st.session_state.rpi_statuses = {}
        for rpi_name, rpi_info in RPIS.items():
            st.session_state.rpi_statuses[rpi_name] = get_rpi_status(rpi_info["url"])
        st.session_state.need_refresh = False
    
    st.markdown("---")
    
    # File Receiver Status (from session state)
    receiver_stats = st.session_state.receiver_stats
    if receiver_stats:
        st.success("✅ File Receiver Online")
        st.metric("Files Received", receiver_stats.get("files_received", 0))
    else:
        st.error("❌ File Receiver Offline")
    
    st.markdown("---")
    
    # RPi Status (from session state)
    st.subheader("Raspberry Pis")
    
    rpi_statuses = st.session_state.rpi_statuses
    total_active_samples = 0
    
    for rpi_name, rpi_info in RPIS.items():
        status = rpi_statuses.get(rpi_name) if rpi_statuses else None
        
        if status:
            st.success(f"✅ {rpi_name}")
            st.text(f"  Channels: {status['total_channels']}")
            st.text(f"  Active: {status['active_samples']}/{status['total_samples_capacity']}")
            total_active_samples += status['active_samples']
        else:
            st.error(f"❌ {rpi_name} (Offline)")
    
    st.markdown("---")
    st.metric("Total Active Samples", total_active_samples)

# ==================== Main Tabs ====================

tab1, tab2, tab3, tab4 = st.tabs([
    "📝 New Measurement",
    "📊 Active Measurements", 
    "📁 Data Browser",
    "📈 Data Visualization"
])

# ==================== Tab 1: New Measurement ====================

with tab1:
    st.header("Configure New Sample Measurement")
    
    # Use a form to prevent reruns on every input change
    with st.form("new_measurement_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sample Information")
            
            sample_id = st.text_input(
                "Sample ID *",
                placeholder="e.g., Sample_001",
                help="Unique identifier (used as folder name)"
            )
            
            cell_area = st.number_input(
                "Cell Area (cm²) *",
                min_value=0.01,
                max_value=10.0,
                value=0.09,
                step=0.01,
                format="%.3f"
            )
            
            current_limit = st.number_input(
                "Current Limit (mA) *",
                min_value=1.0,
                max_value=1000.0,
                value=50.0,
                step=1.0
            )
        
        with col2:
            st.subheader("IV Sweep Parameters")
            
            start_voltage = st.number_input(
                "Start Voltage (V) *",
                min_value=0.0,
                max_value=2.0,
                value=0.0,
                step=0.01,
                format="%.3f"
            )
            
            stop_voltage = st.number_input(
                "Stop Voltage (V) *",
                min_value=0.0,
                max_value=2.0,
                value=1.2,
                step=0.01,
                format="%.3f"
            )
            
            voltage_step = st.number_input(
                "Voltage Step (V) *",
                min_value=0.001,
                max_value=0.1,
                value=0.01,
                step=0.001,
                format="%.3f"
            )
            
            settle_time = st.number_input(
                "Settle Time (s) *",
                min_value=0.001,
                max_value=1.0,
                value=0.1,
                step=0.01,
                format="%.3f"
            )
            
            sweep_interval = st.number_input(
                "IV Sweep Interval (minutes) *",
                min_value=1,
                max_value=1000,
                value=60,
                step=1,
                help="How often to perform IV sweep (1-1000 minutes)"
            )
        
        st.markdown("---")
        
        # Hardware Assignment
        st.subheader("Hardware Assignment")
        
        col3, col4 = st.columns(2)
        
        with col3:
            selected_rpi_name = st.selectbox(
                "Select Raspberry Pi *",
                options=[name for name, info in RPIS.items() if rpi_statuses.get(name)],
                help="Only online RPis shown"
            )
            
            if selected_rpi_name:
                rpi_info = RPIS[selected_rpi_name]
                rpi_id = rpi_info["id"]
                
                # Clear cache and read fresh status files to find used channels
                st.cache_data.clear()
                used_channels = read_all_status_files()
                
                # Find next available channel for this RPi
                start_channel = get_next_available_channel(rpi_id, used_channels)
                
                if start_channel is not None:
                    used_count = len(used_channels.get(rpi_id, [])) // 4
                    st.success(f"✅ **Assigned Channels:** {start_channel}-{start_channel+3}")
                    st.info(f"📊 **Samples in use:** {used_count}/24 on {rpi_info['id']}")
                else:
                    st.warning("⚠️ All 24 slots (96 channels) are occupied on this RPi")
                    start_channel = None
        
        with col4:
            st.info("""
            **Sample Configuration:**
            - Each sample = **4 pixels** (a, b, c, d)
            - Uses **4 consecutive channels**
            - IV sweep runs **every 1 hour**
            - Data auto-transfers to Main PC
            
            **Total Capacity:**
            - 24 samples per RPi
            - 72 samples total (3 RPis)
            """)
        
        st.markdown("---")
        
        # Start Button (inside form)
        submitted = st.form_submit_button("🚀 Start Measurement", type="primary", use_container_width=True)
    
    # Handle form submission (outside form)
    if submitted:
        if not sample_id:
            st.error("❌ Please enter a Sample ID")
        elif start_channel is None:
            st.error("❌ No available slots")
        else:
            config = {
                "sample_id": sample_id,
                "start_channel": start_channel,
                "cell_area": cell_area,
                "current_limit": current_limit,
                "start_voltage": start_voltage,
                "stop_voltage": stop_voltage,
                "voltage_step": voltage_step,
                "settle_time": settle_time,
                "sweep_interval_minutes": sweep_interval,
                "measurement_type": "iv_sweep"
            }
            
            with st.spinner(f"Starting measurement on {selected_rpi_name}..."):
                success, result = start_measurement(rpi_info["url"], config)
                
                if success:
                    st.success(f"✅ Measurement started!")
                    st.json(result)
                    
                    # Create folder structure
                    sample_folder = DATA_ROOT / sample_id
                    for pixel in ['a', 'b', 'c', 'd']:
                        (sample_folder / pixel).mkdir(parents=True, exist_ok=True)
                    
                    st.info(f"📁 Data folder created: `{sample_folder}`")
                    st.cache_data.clear()  # Clear cache to refresh status
                    time.sleep(1)
                    st.rerun()
                else:
                        st.error(f"❌ Failed to start measurement")
                        st.json(result)

# ==================== Tab 2: Active Measurements ====================

with tab2:
    st.header("Active Measurements")
    
    col_refresh, col_filter = st.columns([1, 3])
    with col_refresh:
        if st.button("🔄 Refresh", key="refresh_active"):
            st.cache_data.clear()
            st.rerun()
    
    # Read status files directly (more efficient than API calls)
    all_samples = []
    for rpi_name, rpi_info in RPIS.items():
        rpi_id = rpi_info["id"]
        status_file = DATA_ROOT / f"{rpi_id}_Samples_Status.txt"
        
        if status_file.exists():
            try:
                with open(status_file, 'r') as f:
                    content = f.read()
                    in_data_section = False
                    
                    for line in content.split('\n'):
                        line = line.strip()
                        
                        if line.startswith('-'):
                            in_data_section = True
                            continue
                        
                        if in_data_section and line and not line.startswith('No active'):
                            parts = line.split()
                            if len(parts) >= 4:
                                sample_id = parts[0]
                                channels = parts[1]
                                interval = parts[2] + " " + parts[3]
                                status = parts[4] if len(parts) > 4 else "Running"
                                
                                all_samples.append({
                                    "rpi_name": rpi_name,
                                    "rpi_id": rpi_id,
                                    "sample_id": sample_id,
                                    "channels": channels,
                                    "interval": interval,
                                    "status": status
                                })
            except Exception as e:
                st.error(f"Error reading {rpi_id} status: {e}")
    
    # Display summary
    st.metric("Total Active Samples", len(all_samples))
    
    # Filter by RPi
    with col_filter:
        filter_rpi = st.selectbox(
            "Filter by RPi",
            options=["All"] + list(RPIS.keys()),
            key="filter_rpi"
        )
    
    # Pagination
    items_per_page = 10
    if 'active_page' not in st.session_state:
        st.session_state.active_page = 0
    
    # Apply filter
    if filter_rpi != "All":
        filtered_samples = [s for s in all_samples if s["rpi_name"] == filter_rpi]
    else:
        filtered_samples = all_samples
    
    total_pages = max(1, (len(filtered_samples) + items_per_page - 1) // items_per_page)
    start_idx = st.session_state.active_page * items_per_page
    end_idx = min(start_idx + items_per_page, len(filtered_samples))
    page_samples = filtered_samples[start_idx:end_idx]
    
    # Display samples
    if page_samples:
        for sample in page_samples:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.text(f"📦 {sample['sample_id']}")
                st.caption(f"📡 {sample['rpi_name']}")
            
            with col2:
                st.text(f"📍 Channels: {sample['channels']}")
            
            with col3:
                st.text(f"⏱️ {sample['interval']}")
            
            with col4:
                rpi_info = RPIS[sample['rpi_name']]
                if st.button("⏹️", key=f"stop_{sample['rpi_id']}_{sample['sample_id']}"):
                    if stop_measurement(rpi_info["url"], sample['sample_id']):
                        st.success("✅ Stopped")
                        st.cache_data.clear()
                        time.sleep(0.5)
                        st.rerun()
            
            st.divider()
        
        # Pagination controls
        col_prev, col_info, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("⬅️ Previous", disabled=(st.session_state.active_page == 0)):
                st.session_state.active_page -= 1
                st.rerun()
        with col_info:
            st.text(f"Page {st.session_state.active_page + 1} of {total_pages} ({len(filtered_samples)} samples)")
        with col_next:
            if st.button("Next ➡️", disabled=(st.session_state.active_page >= total_pages - 1)):
                st.session_state.active_page += 1
                st.rerun()
    else:
        st.info("✨ No active measurements")
    
    st.markdown("---")

# ==================== Tab 3: Data Browser ====================

with tab3:
    st.header("📁 Data Browser")
    
    # Efficient directory listing with caching
    @st.cache_data(ttl=30)
    def get_sample_folders():
        try:
            return sorted([f.name for f in DATA_ROOT.iterdir() if f.is_dir()])
        except:
            return []
    
    sample_names = get_sample_folders()
    
    col_search, col_stats = st.columns([3, 1])
    with col_search:
        search_term = st.text_input("🔍 Search Samples", placeholder="Type to filter...")
    with col_stats:
        st.metric("Total Samples", len(sample_names))
    
    # Filter samples
    if search_term:
        filtered_samples = [s for s in sample_names if search_term.lower() in s.lower()]
    else:
        filtered_samples = sample_names
    
    if filtered_samples:
        # Pagination for sample list
        items_per_page_browser = 20
        if 'browser_page' not in st.session_state:
            st.session_state.browser_page = 0
        
        total_pages_browser = max(1, (len(filtered_samples) + items_per_page_browser - 1) // items_per_page_browser)
        start_idx_browser = st.session_state.browser_page * items_per_page_browser
        end_idx_browser = min(start_idx_browser + items_per_page_browser, len(filtered_samples))
        page_samples_browser = filtered_samples[start_idx_browser:end_idx_browser]
        
        selected_sample = st.selectbox(
            "Select Sample", 
            options=page_samples_browser,
            key="sample_selector"
        )
        
        # Pagination controls
        col_prev_b, col_info_b, col_next_b = st.columns([1, 2, 1])
        with col_prev_b:
            if st.button("⬅️ Prev", key="prev_browser", disabled=(st.session_state.browser_page == 0)):
                st.session_state.browser_page -= 1
                st.rerun()
        with col_info_b:
            st.text(f"Page {st.session_state.browser_page + 1} of {total_pages_browser} ({len(filtered_samples)} samples)")
        with col_next_b:
            if st.button("Next ➡️", key="next_browser", disabled=(st.session_state.browser_page >= total_pages_browser - 1)):
                st.session_state.browser_page += 1
                st.rerun()
        
        st.markdown("---")
        
        if selected_sample:
            sample_path = DATA_ROOT / selected_sample
            
            st.subheader(f"📦 {selected_sample}")
            st.caption(f"📂 {sample_path}")
            
            # Check if Config.txt exists
            config_file = sample_path / "Config.txt"
            if config_file.exists():
                with st.expander("📄 View Config.txt"):
                    st.code(config_file.read_text(), language="text")
            
            # Show pixels
            cols = st.columns(4)
            
            for idx, pixel in enumerate(['a', 'b', 'c', 'd']):
                with cols[idx]:
                    st.markdown(f"### Pixel {pixel.upper()}")
                    
                    pixel_dir = sample_path / pixel
                    if pixel_dir.exists():
                        files = sorted(pixel_dir.glob("*.csv"))
                        
                        if files:
                            st.success(f"✅ {len(files)} files")
                            latest_file = files[-1]
                            st.caption(f"Latest: {latest_file.name}")
                        else:
                            st.warning("⚠️ No files")
                    else:
                        st.warning("⚠️ No data")
    else:
        st.info("No samples found. Start a measurement to create data.")

# ==================== Tab 4: Data Visualization ====================

with tab4:
    st.header("📈 Data Visualization")
    
    sample_folders = [f for f in DATA_ROOT.iterdir() if f.is_dir()]
    
    if sample_folders:
        sample_names = sorted([f.name for f in sample_folders])
        viz_sample = st.selectbox("Select Sample for Visualization", options=sample_names, key="viz_sample")
        
        if viz_sample:
            sample_path = DATA_ROOT / viz_sample
            
            pixel_to_plot = st.radio("Select Pixel", ['a', 'b', 'c', 'd'], horizontal=True)
            
            pixel_dir = sample_path / pixel_to_plot
            if pixel_dir.exists():
                files = sorted(list(pixel_dir.glob("*.csv")))
                
                if files:
                    file_to_plot = st.selectbox("Select File", [f.name for f in files])
                    
                    if file_to_plot:
                        df = pd.read_csv(pixel_dir / file_to_plot)
                        
                        if 'voltage' in df.columns and 'current' in df.columns:
                            # IV Curve
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=df['voltage'],
                                y=df['current'] * 1000,  # Convert to mA
                                mode='lines+markers',
                                name='IV Curve'
                            ))
                            fig.update_layout(
                                title=f"IV Curve: {viz_sample} - Pixel {pixel_to_plot.upper()}",
                                xaxis_title="Voltage (V)",
                                yaxis_title="Current (mA)",
                                template="plotly_white"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Power Curve
                            if 'power' in df.columns or ('voltage' in df.columns and 'current' in df.columns):
                                power = df['power'] if 'power' in df.columns else df['voltage'] * df['current']
                                
                                fig2 = go.Figure()
                                fig2.add_trace(go.Scatter(
                                    x=df['voltage'],
                                    y=power * 1000,  # Convert to mW
                                    mode='lines+markers',
                                    name='Power',
                                    line=dict(color='red')
                                ))
                                fig2.update_layout(
                                    title=f"Power Curve: {viz_sample} - Pixel {pixel_to_plot.upper()}",
                                    xaxis_title="Voltage (V)",
                                    yaxis_title="Power (mW)",
                                    template="plotly_white"
                                )
                                st.plotly_chart(fig2, use_container_width=True)
                                
                                # Show key metrics
                                max_power = power.max() * 1000
                                max_power_voltage = df.loc[power.idxmax(), 'voltage']
                                
                                col1, col2, col3 = st.columns(3)
                                col1.metric("Max Power", f"{max_power:.2f} mW")
                                col2.metric("Voltage @ MPP", f"{max_power_voltage:.3f} V")
                                col3.metric("Data Points", len(df))
                            
                            # Show raw data
                            if st.checkbox("Show Raw Data"):
                                st.dataframe(df)
                        else:
                            st.error("Invalid data format")
                else:
                    st.warning("No files available for this pixel")
            else:
                st.warning("No data directory for this pixel")
    else:
        st.info("No data available for visualization")

# ==================== Footer ====================

st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: gray;'>
    <p>OctoBoard Control Center v2.0 | Data: {DATA_ROOT} | Active Samples: {total_active_samples}/72</p>
</div>
""", unsafe_allow_html=True)

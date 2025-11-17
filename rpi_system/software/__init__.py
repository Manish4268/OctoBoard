__version__ = "0.1.0"

# Lazy imports to allow setting SIMULATION_MODE first
def _import_hardware():
    from .hardware import OBoardManager, OBoard, Channel, Softdac
    return OBoardManager, OBoard, Channel, Softdac

# For backward compatibility, import immediately if simulation mode is set
import os
if os.environ.get('OCTOBOARD_SIMULATION', '').lower() in ('true', '1', 'yes'):
    OBoardManager, OBoard, Channel, Softdac = _import_hardware()
else:
    # Defer imports until explicitly called
    OBoardManager = None
    OBoard = None
    Channel = None
    Softdac = None
    
def get_hardware_classes():
    """Get hardware classes after environment is set up."""
    return _import_hardware()

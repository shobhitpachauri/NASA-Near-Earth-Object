import numpy as np
import h5py
from typing import Dict, Optional
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThesanLoader:
    """Loader for THESAN simulation data"""
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        self._validate_path()
        
    def _validate_path(self):
        if not os.path.exists(self.base_path):
            raise FileNotFoundError(f"THESAN data path not found: {self.base_path}")
            
    def load_snapshot(self, snapshot_num: int) -> Dict[str, np.ndarray]:
        """Load a THESAN snapshot"""
        filename = f"{self.base_path}/snap_{snapshot_num:03d}.hdf5"
        logger.info(f"Loading snapshot: {filename}")
        
        try:
            with h5py.File(filename, 'r') as f:
                data = {
                    'density': f['PartType0/Density'][:],
                    'temperature': f['PartType0/Temperature'][:],
                    'neutral_fraction': f['PartType0/NeutralHydrogenFraction'][:]
                }
            return data
        except Exception as e:
            logger.error(f"Error loading snapshot {snapshot_num}: {str(e)}")
            raise 
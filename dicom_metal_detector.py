import sys
import os
import csv
import logging
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

# Forensic-Hardened Version (3r-222/26 Context)

# Setup forensic logging
log_dir = Path("H:/ACTOR_DEV_ENV/logs")
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "dicom_detector_audit.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("dicom_hardened")

def _log_forensic_detection(file_path: str, metal_pixels: int):
    """Log detection with SHA-256 integrity hash."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "file": os.path.basename(file_path),
        "metal_pixels": metal_pixels,
        "status": "DETECTION"
    }
    serialized_entry = json.dumps(entry, sort_keys=True)
    integrity_hash = hashlib.sha256(serialized_entry.encode()).hexdigest()
    entry["integrity_hash"] = integrity_hash
    
    logger.info("Forensic Detection: %s", json.dumps(entry))

try:
    import pydicom
    import numpy as np
except ImportError as e:
    logger.critical(f"Library import failed: {e}")
    sys.exit(1)

registry_csv = Path(r"H:\ACTOR_DEV_ENV\DICOM_Final_Metadata_Registry.csv")
METAL_HU_THRESHOLD = 2000
MIN_PIXELS_FOR_BOLT = 50

logger.info(f"Starting forensic DICOM density detector (HU > {METAL_HU_THRESHOLD})")

january_files = []
march_files = []

# Validate registry access
if not registry_csv.exists():
    logger.critical(f"Registry file not found: {registry_csv}")
    sys.exit(1)

try:
    with open(registry_csv, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) < 4: continue
            path, _, _, study_date = row
            if "20220109" in study_date:
                january_files.append(path)
            elif "20220314" in study_date:
                march_files.append(path)
except Exception as e:
    logger.error(f"Error reading registry: {e}")
    sys.exit(1)

def analyze_metal_in_dicom(file_paths, period_name):
    logger.info(f"--- Analyzing {period_name} (Files: {len(file_paths)}) ---")
    files_with_metal = 0

    for f in file_paths:
        try:
            ds = pydicom.dcmread(f)
            if not hasattr(ds, 'pixel_array'):
                continue

            pixels = ds.pixel_array.astype(np.float64)
            intercept = getattr(ds, 'RescaleIntercept', 0)
            slope = getattr(ds, 'RescaleSlope', 1)
            hu_image = pixels * slope + intercept
            metal_pixels = np.sum(hu_image > METAL_HU_THRESHOLD)

            if metal_pixels > MIN_PIXELS_FOR_BOLT:
                files_with_metal += 1
                _log_forensic_detection(f, int(metal_pixels))

        except Exception as e:
            logger.warning(f"Error analyzing file {f}: {e}")

    logger.info(f"SUMMARY {period_name}: Detections: {files_with_metal} / Total: {len(file_paths)}")

# Launch analysis
analyze_metal_in_dicom(january_files, "JANUARY (09.01.2022)")
analyze_metal_in_dicom(march_files, "MARCH (14.03.2022)")
logger.info("Forensic analysis complete.")

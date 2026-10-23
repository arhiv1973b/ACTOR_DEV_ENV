import os
import hashlib
import datetime
import pydicom
from typing import Dict, Any, Optional

class TimeMarkerForensic:
    """
    Implements the Time-Marker Protocol for CASE-MACHERET-1997-2026.
    Focuses on extraction, hash correlation, and consistency checking.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.report: Dict[str, Any] = {
            "file_path": file_path,
            "status": "NOT_STARTED",
            "fixation_hash": None,
            "timestamps": {},
            "anomalies": []
        }

    def fixate_state(self) -> str:
        """Fixates the file state using SHA-256."""
        sha256_hash = hashlib.sha256()
        with open(self.file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        self.report["fixation_hash"] = sha256_hash.hexdigest()
        return self.report["fixation_hash"]

    def extract_fs_metadata(self):
        """Extracts file system timestamps."""
        stat = os.stat(self.file_path)
        self.report["timestamps"]["fs_mtime"] = datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
        self.report["timestamps"]["fs_ctime"] = datetime.datetime.fromtimestamp(stat.st_ctime).isoformat()

    def extract_dicom_metadata(self) -> bool:
        """Extracts DICOM specific timestamps if applicable."""
        try:
            ds = pydicom.dcmread(self.file_path, stop_before_pixels=True)
            # Instance Creation Date (0008,0012) and Time (0008,0013)
            creation_date = ds.get((0x0008, 0x0012), None)
            creation_time = ds.get((0x0008, 0x0013), None)
            
            if creation_date and creation_time:
                dt_str = f"{creation_date.value}{creation_time.value}"
                # DICOM date format is YYYYMMDD, time is HHMMSS.FFFFFF
                self.report["timestamps"]["dicom_creation"] = dt_str
                return True
        except Exception as e:
            # Not a DICOM file or error reading
            pass
        return False

    def verify_consistency(self):
        """Compares internal metadata with FS timestamps."""
        fs_mtime = self.report["timestamps"].get("fs_mtime")
        dicom_creation = self.report["timestamps"].get("dicom_creation")

        if dicom_creation and fs_mtime:
            # Basic string comparison or partial match logic
            # DICOM: 20260115... vs FS: 2026-01-15...
            normalized_dicom = dicom_creation[:8] # YYYYMMDD
            normalized_fs = fs_mtime.replace("-", "")[:8]
            
            if normalized_dicom != normalized_fs:
                self.report["anomalies"].append({
                    "type": "TIMESTAMP_MISMATCH",
                    "details": f"DICOM creation ({normalized_dicom}) != FS mtime ({normalized_fs})"
                })
                self.report["status"] = "TAMPERED"
            else:
                self.report["status"] = "VERIFIED"
        else:
            self.report["status"] = "INCOMPLETE_DATA"

    def run_audit(self) -> Dict[str, Any]:
        """Executes the full protocol."""
        self.fixate_state()
        self.extract_fs_metadata()
        is_dicom = self.extract_dicom_metadata()
        self.verify_consistency()
        return self.report

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
        forensic = TimeMarkerForensic(path)
        result = forensic.run_audit()
        import json
        print(json.dumps(result, indent=2))

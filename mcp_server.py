import json, os, logging
from mcp.server.fastmcp import FastMCP
from model_orchestrator import ModelOrchestrator
from mcp_utils import run_ps
from mcp_drive_indexer import DatabaseManager, DiskScanner, InferenceOrchestrator, DriveWorkerPool

# Полностью отключаем любые логи, чтобы они не попали в поток stdout
logging.disable(logging.CRITICAL)

mcp = FastMCP("tiula-bridge")
orchestrator = ModelOrchestrator()
db_manager = DatabaseManager()
inference_orchestrator = InferenceOrchestrator()

@mcp.tool()
def sign_artifact(artifact_path: str):
    return run_ps(r'H:\ACTOR_DEV_ENV\tiula-crypto-sandbox.psm1', 'Sign-Artifact', 
                  {'ArtifactPath': artifact_path, 'PrivateKeyPath': r'H:\ACTOR_DEV_ENV\keys\actor_ed25519', 'SignaturePath': r'H:\ACTOR_DEV_ENV\test.txt.sig'})

@mcp.tool()
def verify_artifact(artifact_path: str):
    return run_ps(r'H:\ACTOR_DEV_ENV\tiula-crypto-sandbox.psm1', 'Verify-ArtifactSignature', 
                  {'ArtifactPath': artifact_path, 'PublicKeyPath': r'H:\ACTOR_DEV_ENV\keys\actor_ed25519.pub', 'SignaturePath': r'H:\ACTOR_DEV_ENV\test.txt.sig'})

@mcp.tool()
def run_model(model_type: str, audit_events: list):
    """Executes a TI-ULA model via MOP."""
    return orchestrator.run_model(model_type, audit_events)

@mcp.tool()
def scan_and_index_drive(root_path: str):
    """Scans and indexes filesystem paths into SQLite queue with SHA-256."""
    scanner = DiskScanner(root_path, db_manager)
    scanner.scan()
    return {"status": "success", "message": f"Completed scanning {root_path}"}

@mcp.tool()
def process_index_batch(max_workers: int = 4, limit: int = 100):
    """Processes pending files in parallel using light local model (qwen2.5:0.5b)."""
    pool = DriveWorkerPool(db_manager, inference_orchestrator, max_workers=max_workers)
    pool.run_pool(batch_limit=limit)
    return {"status": "success", "message": f"Processed batch of up to {limit} files with {max_workers} workers."}

@mcp.tool()
def get_daily_escalation_report():
    """Returns daily load and escalation statistics report grouped by date."""
    return db_manager.get_daily_load_report()

# Запуск в тихом режиме
if __name__ == "__main__":
    mcp.run()

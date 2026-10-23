import json, os
from mcp.server.fastmcp import FastMCP
from model_orchestrator import ModelOrchestrator
from mcp_utils import run_ps

mcp = FastMCP("tiula-bridge")
orchestrator = ModelOrchestrator()

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

if __name__ == "__main__":
    mcp.run()
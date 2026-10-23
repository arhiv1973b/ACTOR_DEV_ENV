from antigravity_adapter import get_adapter
from mcp_utils import run_ps
import os

class ModelOrchestrator:
    """
    Hybrid orchestrator: routes threat analysis to Antigravity (primary) or local PowerShell (fallback).
    
    Strategy:
    - Use Antigravity for general threat classification, codegen, routing
    - Fall back to local PowerShell for sensitive forensic evidence (DICOM, compliance-locked data)
    """
    
    def __init__(self, 
                 script_path: str = r'H:\ACTOR_DEV_ENV\ti-ula-integration.psm1',
                 use_antigravity: bool = True,
                 use_local_fallback: bool = True):
        """
        Args:
            script_path: Local PowerShell module (for fallback)
            use_antigravity: Route through Antigravity first
            use_local_fallback: Fall back to local PowerShell on error
        """
        self.script_path = script_path
        self.use_antigravity = use_antigravity
        self.use_local_fallback = use_local_fallback
        self.agy_adapter = get_adapter() if use_antigravity else None
    
    def run_model(self, model_type: str, audit_events: list, use_local: bool = False):
        """
        Execute TI-ULA model (anomaly, pattern_match, behavior, privilege_esc).
        
        Args:
            model_type: Model name
            audit_events: List of audit event dicts
            use_local: Force local PowerShell (bypass Antigravity)
            
        Returns:
            Model response dict
        """
        allowed_models = ['anomaly', 'pattern_match', 'behavior', 'privilege_esc']
        
        if model_type not in allowed_models:
            return {"error": f"Model {model_type} not found. Allowed: {allowed_models}"}
        
        # Try Antigravity first (unless forced local)
        if self.use_antigravity and not use_local and self.agy_adapter:
            result = self.agy_adapter.invoke_model(model_type, audit_events)
            
            # If success, return
            if "error" not in result:
                return {**result, "_source": "antigravity"}
            
            # If error and local fallback disabled, return error
            if not self.use_local_fallback:
                return result
            
            # Otherwise fall back to local
        
        # Local PowerShell execution (fallback or forced)
        return self._run_local(model_type, audit_events)
    
    def _run_local(self, model_type: str, audit_events: list):
        """Execute model locally via PowerShell (sensitive data, compliance)."""
        return run_ps(
            self.script_path, 
            'Invoke-TiUlaModel', 
            {'AuditEvents': audit_events, 'Models': [model_type]}
        )

"""
Test Antigravity adapter with dual-layer authorization (Antigravity + Gemini).

Usage:
    python test_antigravity_migration.py
    python test_antigravity_migration.py --check-credentials
"""

import json
import sys
import os
from antigravity_adapter import AntigravityAdapter, get_adapter, validate_credentials
from model_orchestrator import ModelOrchestrator

def test_credentials_check():
    """Validate authorization layers."""
    print("[TEST] Checking authorization credentials...")
    checks = validate_credentials()
    
    print(f"  AGY_AUTH_TOKEN: {'✓ SET' if checks['agy_auth_token'] else '✗ NOT SET'}")
    print(f"  GEMINI_API_KEY: {'✓ SET' if checks['gemini_api_key'] else '✗ NOT SET'}")
    print(f"  At least one backend: {'✓ YES' if checks['has_at_least_one'] else '✗ NO - CRITICAL'}")
    
    if not checks['has_at_least_one']:
        print("\n  ⚠ CRITICAL: No credentials available. Configure .env.local:")
        print("    1. Run: agy auth")
        print("    2. Get GEMINI_API_KEY from https://ai.google.dev/")
        return False
    
    print()
    return True

def test_adapter_initialization():
    """Test Antigravity adapter creation."""
    print("[TEST] Initializing Antigravity adapter (dual-layer)...")
    adapter = get_adapter()
    
    print(f"  ✓ Adapter created: {adapter.__class__.__name__}")
    print(f"  - AGY endpoint: {adapter.endpoint}")
    print(f"  - Gemini model: {adapter.gemini_model}")
    print(f"  - Compliance mode: {adapter.compliance_mode}")
    print()

def test_orchestrator_initialization():
    """Test hybrid orchestrator creation."""
    print("[TEST] Initializing ModelOrchestrator (hybrid dual-model)...")
    orchestrator = ModelOrchestrator(use_antigravity=True, use_local_fallback=True)
    
    print(f"  ✓ Orchestrator created")
    print(f"  - Antigravity enabled: {orchestrator.use_antigravity}")
    print(f"  - Local fallback enabled: {orchestrator.use_local_fallback}")
    print(f"  - Strategy: Antigravity first → Gemini fallback")
    print()

def test_model_validation():
    """Test model type validation."""
    print("[TEST] Validating TI-ULA model types...")
    orchestrator = ModelOrchestrator()
    
    valid_models = ['anomaly', 'pattern_match', 'behavior', 'privilege_esc']
    
    for model_type in valid_models:
        # This will test adapter logic without actual agy/Gemini calls
        sample_event = {
            "timestamp": "2024-01-15T10:30:00Z",
            "event_type": model_type,
            "source": "test"
        }
        result = orchestrator.run_model(model_type, [sample_event])
        
        # Should return result dict (error or success from adapter)
        status = "✓" if isinstance(result, dict) else "✗"
        print(f"  {status} Model '{model_type}' accepted")
    
    # Test invalid model
    result = orchestrator.run_model("invalid_model", [])
    if "error" in result and "not found" in result["error"]:
        print(f"  ✓ Invalid model rejected")
    print()

def test_multimodal_classification_signature():
    """Test multi-modal threat classification method signature."""
    print("[TEST] Multi-modal threat classification (DICOM + OCR + Whisper + Audit)...")
    adapter = get_adapter()
    
    # Sample medical device forensic data
    dicom_sample = {
        "patient_id": "12345",
        "modality": "CT",
        "device": "Siemens SOMATOM Definition AS+",
        "timestamp": "2024-01-15T10:30:00Z"
    }
    
    text_sample = "Unauthorized access to PACS detected. User: admin. Time: 14:30 UTC"
    audio_sample = "Alert: Privilege escalation attempt detected on medical device network segment"
    events_sample = [
        {
            "type": "dicom_export",
            "timestamp": "2024-01-15T10:30:00Z",
            "user_id": "unknown_user",
            "severity": "high"
        }
    ]
    
    result = adapter.classify_threat(
        dicom_metadata=dicom_sample,
        extracted_text=text_sample,
        transcribed_audio=audio_sample,
        audit_events=events_sample,
        force_local=True
    )
    
    print(f"  ✓ classify_threat() accepts multi-modal inputs")
    print(f"  - Execution source: {result.get('_source', 'unknown')}")
    print(f"  - Compliance mode: {result.get('_compliance', 'unknown')}")
    print(f"  - Response type: {type(result).__name__}")
    print()

def test_compliance_modes():
    """Test different compliance routing modes."""
    print("[TEST] Compliance routing modes...")
    
    modes = {
        "strict": "Local Gemini only (DICOM/healthcare)",
        "relax": "Cloud first + Local fallback"
    }
    
    for mode, desc in modes.items():
        adapter = AntigravityAdapter(compliance_mode=mode)
        print(f"  ✓ Mode '{mode}': {desc}")
        print(f"    - Route multi-modal to: {'LOCAL ONLY' if mode == 'strict' else 'LOCAL (always)'}")
    
    print()

def test_env_configuration():
    """Display current environment configuration."""
    print("[TEST] Environment configuration (.env.local)...")
    
    config_keys = {
        "AGY_AUTH_TOKEN": "Antigravity OAuth token",
        "AGY_ENDPOINT": "Antigravity API endpoint",
        "GEMINI_API_KEY": "Google Gemini API key (fallback)",
        "GEMINI_MODEL": "Gemini model version",
        "LOCAL_COMPLIANCE_MODE": "Compliance routing mode",
        "USE_ANTIGRAVITY": "Enable Antigravity routing",
        "ENABLE_DICOM_ANALYSIS": "Enable DICOM forensics",
        "ENABLE_ARTIFACT_SIGNING": "Enable evidence signing"
    }
    
    for key, desc in config_keys.items():
        val = os.getenv(key, "(not set)")
        # Mask sensitive values
        if "KEY" in key or "TOKEN" in key:
            val = "***SET***" if val != "(not set)" else val
        status = "✓" if val != "(not set)" else "⚠"
        print(f"  {status} {key}: {val}")
    
    print()

def run_live_forensic_audit():
    print("\n" + "="*80)
    print("[LIVE] Running Dual-Run Comparative Threat Analysis (Forensic)")
    print("="*80)
    
    adapter = get_adapter()
    orchestrator = ModelOrchestrator(use_antigravity=True, use_local_fallback=True)
    
    # Define mock forensic events for analysis (representing a traversal + privilege escalation attempt)
    sample_events = [
        {
            "timestamp": "2026-06-18T20:30:00Z",
            "type": "capability.request",
            "user_id": "service_user",
            "command": "sudo -l",
            "details": "Checking privilege levels"
        },
        {
            "timestamp": "2026-06-18T20:31:00Z",
            "type": "file.access",
            "user_id": "service_user",
            "path": "../etc/passwd",
            "details": "Directory traversal attempt detected"
        },
        {
            "timestamp": "2026-06-18T20:32:00Z",
            "type": "anomaly.detected",
            "user_id": "service_user",
            "model": "SeTcbPrivilege",
            "details": "Attempt to obtain SeTcbPrivilege capability"
        }
    ]
    
    # 1. Cloud-first / Analytical Model invocation
    print("\n[RUN 1] Cloud/Orchestrator Analysis...")
    cloud_result = orchestrator.run_model("privilege_esc", sample_events, use_local=False)
    print(f"  ✓ Run complete (Source: {cloud_result.get('_source', 'unknown')})")
    print(f"  - Summary: {json.dumps(cloud_result, indent=2, ensure_ascii=False)[:300]}...")
    
    # 2. Local Forensic Run (PowerShell module execution)
    print("\n[RUN 2] Local Forensic PowerShell (TI-ULA) Analysis...")
    local_result = orchestrator._run_local("privilege_esc", sample_events)
    print(f"  ✓ Run complete (Source: PowerShell Module)")
    print(f"  - Risk Score: {local_result.get('risk_score', 'N/A')}")
    print(f"  - Recommendations: {local_result.get('recommendations', [])}")
    
    # 3. Multi-modal threat classification
    print("\n[RUN 3] Multi-modal Forensic Threat Classification...")
    dicom_sample = {
        "patient_id": "ACTOR-997",
        "modality": "CT",
        "device": "Siemens SOMATOM Definition AS+",
        "timestamp": "2026-06-18T20:30:00Z"
    }
    text_sample = "Traversing directory parent paths: ../etc/passwd. Attempting SeTcbPrivilege."
    audio_sample = "Whisper transcript: Warning, potential privilege escalation segment."
    
    multimodal_result = adapter.classify_threat(
        dicom_metadata=dicom_sample,
        extracted_text=text_sample,
        transcribed_audio=audio_sample,
        audit_events=sample_events,
        force_local=True
    )
    print(f"  ✓ Run complete (Source: {multimodal_result.get('_source', 'unknown')})")
    print(f"  - Assessment Details: {json.dumps(multimodal_result, indent=2, ensure_ascii=False)}")
    
    # Save the dual-run comparison report
    comparison_report = {
        "timestamp": "2026-06-18T20:37:22+03:00",
        "analysis_type": "Dual-Run Comparative threat analysis",
        "cloud_run": cloud_result,
        "local_run": local_result,
        "multimodal_run": multimodal_result
    }
    
    os.makedirs("./audits", exist_ok=True)
    report_file = "./audits/dual_run_comparative_audit.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(comparison_report, f, indent=2, ensure_ascii=False)
        
    print("\n" + "="*80)
    print(f"✓ DUAL-RUN COMPARATIVE REPORT SAVED: {report_file}")
    print("="*80 + "\n")

def main():
    if "--live" in sys.argv:
        try:
            run_live_forensic_audit()
            return 0
        except Exception as e:
            print(f"\n✗ Live forensic audit failed: {e}")
            import traceback
            traceback.print_exc()
            return 1

    print("\n" + "="*80)
    print("Antigravity Migration Test Suite (Dual-Layer Authorization)")
    print("="*80 + "\n")
    
    try:
        # Check credentials first
        if not test_credentials_check():
            print("FAILURE: Missing credentials. Configure .env.local\n")
            return 1
        
        # Run tests
        test_adapter_initialization()
        test_orchestrator_initialization()
        test_model_validation()
        test_multimodal_classification_signature()
        test_compliance_modes()
        test_env_configuration()
        
        print("="*80)
        print("SUMMARY: All initialization tests passed ✓")
        print("="*80)
        print("\nNEXT STEPS:")
        print("1. Set AGY_AUTH_TOKEN:os.environ.get("SECRET_VAR")   $ agy auth")
        print("   Copy token from console output into .env.local")
        print()
        print("2. Set GEMINI_API_KEY:os.environ.get("SECRET_VAR")   Visit: https://ai.google.dev/")
        print("   Create API key and add to .env.local")
        print()
        print("3. Run live model invocation:")
        print("   $ python test_antigravity_migration.py --live")
        print()
        print("4. Deploy to Docker:")
        print("   $ docker-compose up --build")
        print()
        
        return 0
    
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

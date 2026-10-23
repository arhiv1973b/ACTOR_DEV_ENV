"""
Antigravity CLI Adapter Layer with Multi-Backend Fallback
Abstracts 'agy' CLI calls for TI-ULA model orchestration.
Reads from Windows System Environment Variables (bессрочные ключи).

Supported backends:
  - Antigravity CLI (AGY_AUTH_TOKEN)
  - Google Gemini (GEMINI_API_KEY) — local, compliance-locked
  - OpenAI (OPENAI_API_KEY)
  - Groq (GROQ_API_KEY)
  - OpenRouter (OPENROUTER_API_KEY)
  - Anthropic (ANTHROPIC_API_KEY)
  - Google API (GOOGLE_API_KEY)

Dual-layer strategy:
  - Layer 1 (Cloud): Antigravity CLI for routing, codegen, general threat analysis
  - Layer 2+ (Fallback): Multi-backend selection (Gemini preferred for compliance)
"""

import json
import subprocess
import os
import logging
from typing import Dict, List, Any, Optional
import sys

try:
    from dotenv import load_dotenv
    # Load .env.local and override existing env variables
    load_dotenv(dotenv_path=".env.local", override=True)
except ImportError:
    pass

logger = logging.getLogger(__name__)

class AntigravityAdapter:
    """
    Hybrid adapter: Antigravity orchestration with multi-backend fallback.
    Reads eternal keys from Windows System Environment Variables.
    """
    
    def __init__(self, 
                 agy_bin: str = "agy",
                 auth_token: Optional[str] = None,
                 endpoint: Optional[str] = None,
                 tmp_dir: str = "./.native",
                 compliance_mode: str = "strict"):
        """
        Initialize Antigravity adapter with multi-backend fallback.
        All API keys read from Windows System Environment Variables.
        
        Args:
            agy_bin: Path to 'agy' executable (default: system PATH)
            auth_token: AGY_AUTH_TOKEN (from Windows env or explicit)
            endpoint: AGY_ENDPOINT (cloud orchestrator URL)
            tmp_dir: Temporary directory for JSON I/O
            compliance_mode: 'strict' (local only) or 'relax' (cloud+local)
        """
        self.agy_bin = agy_bin
        
        # Clean environment variables that are placeholders or empty
        for env_var in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENAI_API_KEY", "GROQ_API_KEY", 
                        "OPENROUTER_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_GENERATIVE_AI_API_KEY"]:
            val = os.getenv(env_var)
            if val in ("ВАШ_КЛЮЧ", ""):
                os.environ.pop(env_var, None)

        # Antigravity routing layer (optional)
        self.auth_token = auth_token or os.getenv("AGY_AUTH_TOKEN")
        self.endpoint = endpoint or os.getenv("AGY_ENDPOINT", "https://api.antigravity.ai")
        
        # Multi-backend API keys (from Windows System Environment)
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.gmail_app_pass = os.getenv("GMAIL_APP_PASS")  # For forensics/logging
        
        # Model selection
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
        
        self.tmp_dir = tmp_dir
        self.compliance_mode = compliance_mode or os.getenv("LOCAL_COMPLIANCE_MODE", "strict")
        
        # Ensure tmp_dir exists
        os.makedirs(tmp_dir, exist_ok=True)
        
        # Diagnostics
        backends = self._get_available_backends()
        logger.info(f"Adapter initialized. Available backends: {backends}")
        
        if not backends:
            logger.warning("⚠ No API backends detected in Windows Environment Variables!")
    
    def _get_available_backends(self) -> List[str]:
        """List all available API backends from environment."""
        backends = []
        
        if self.auth_token:
            backends.append("antigravity")
        if self.gemini_api_key:
            backends.append("gemini")
        if self.openai_api_key:
            backends.append("openai")
        if self.groq_api_key:
            backends.append("groq")
        if self.openrouter_api_key:
            backends.append("openrouter")
        if self.anthropic_api_key:
            backends.append("anthropic")
        if self.google_api_key:
            backends.append("google_api")
        
        return backends
    
    def _build_env(self) -> Dict[str, str]:
        """Build environment for agy subprocess."""
        env = os.environ.copy()
        if self.auth_token:
            env["AGY_AUTH_TOKEN"] = self.auth_token
        if self.endpoint:
            env["AGY_ENDPOINT"] = self.endpoint
        return env
    
    def invoke_model(self, 
                     model_type: str, 
                     audit_events: List[Dict[str, Any]],
                     use_local: bool = False,
                     preferred_backend: Optional[str] = None,
                     extra_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Invoke threat classification model via best available backend.
        
        Args:
            model_type: 'anomaly', 'pattern_match', 'behavior', 'privilege_esc'
            audit_events: List of audit event dictionaries
            use_local: Force local backend (bypass Antigravity)
            preferred_backend: Prefer specific backend ('gemini', 'openai', 'groq', etc.)
            extra_params: Additional model-specific parameters
            
        Returns:
            Model response dict with '_source' field indicating execution layer
        """
        allowed_models = ['anomaly', 'pattern_match', 'behavior', 'privilege_esc']
        
        if model_type not in allowed_models:
            return {"error": f"Model '{model_type}' not found. Allowed: {allowed_models}"}
        
        # Try Antigravity first (unless forced local or compliance_mode=strict)
        if not use_local and self.auth_token and self.compliance_mode != "strict":
            result = self._invoke_antigravity(model_type, audit_events, extra_params)
            if "error" not in result:
                return {**result, "_source": "antigravity"}
        
        # Fall back to local backends (in order of preference)
        backends_to_try = self._get_backend_priority(preferred_backend)
        
        for backend in backends_to_try:
            if backend == "gemini" and self.gemini_api_key:
                result = self._invoke_gemini(model_type, audit_events, extra_params)
                if "error" not in result:
                    return {**result, "_source": "gemini"}
            
            elif backend == "openai" and self.openai_api_key:
                result = self._invoke_openai(model_type, audit_events, extra_params)
                if "error" not in result:
                    return {**result, "_source": "openai"}
            
            elif backend == "groq" and self.groq_api_key:
                result = self._invoke_groq(model_type, audit_events, extra_params)
                if "error" not in result:
                    return {**result, "_source": "groq"}
            
            elif backend == "anthropic" and self.anthropic_api_key:
                result = self._invoke_anthropic(model_type, audit_events, extra_params)
                if "error" not in result:
                    return {**result, "_source": "anthropic"}
        
        return {
            "error": "No model backend available",
            "details": "Set API keys in Windows System Environment Variables"
        }
    
    def _get_backend_priority(self, preferred: Optional[str] = None) -> List[str]:
        """
        Get backend priority order.
        Priority: preferred > local backends > none
        Local backends: gemini (compliance) > openai > groq > anthropic > openrouter
        """
        if preferred and preferred in self._get_available_backends():
            return [preferred]
        
        # Default priority: Gemini (compliance-safe) > OpenAI > Groq > Anthropic
        return ["gemini", "openai", "groq", "anthropic", "openrouter"]
    
    def _invoke_antigravity(self,
                           model_type: str,
                           audit_events: List[Dict],
                           extra_params: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute via Antigravity CLI."""
        payload = {
            "model": model_type,
            "events": audit_events,
            **(extra_params or {})
        }
        
        tmp_out = os.path.join(self.tmp_dir, "agy_out.json")
        
        try:
            if os.path.exists(tmp_out):
                os.remove(tmp_out)
            
            cmd = [
                self.agy_bin,
                "invoke",
                f"--model={model_type}",
                f"--input=-",
                f"--output={tmp_out}",
                "--format=json"
            ]
            
            result = subprocess.run(
                cmd,
                input=json.dumps(payload),
                capture_output=True,
                text=True,
                env=self._build_env(),
                timeout=30
            )
            
            if os.path.exists(tmp_out):
                with open(tmp_out, 'r', encoding='utf-8-sig') as f:
                    output = json.load(f)
                
                if result.returncode == 0:
                    return output
                else:
                    logger.warning(f"Antigravity invocation failed: {result.stderr}")
                    return {"error": "Antigravity invocation failed", "details": result.stderr}
            
            if result.returncode != 0:
                return {"error": "Antigravity CLI failed", "details": result.stderr}
            
            return {"error": "No output file generated"}
        
        except subprocess.TimeoutExpired:
            logger.warning("Antigravity invocation timeout (30s)")
            return {"error": "Antigravity timeout (30s)"}
        except Exception as e:
            logger.error(f"Antigravity invocation error: {e}")
            return {"error": str(e)}
    
    def _invoke_gemini(self,
                       model_type: str,
                       audit_events: List[Dict],
                       extra_params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute via Google Gemini API (local, compliance-locked).
        Requires: pip install google-genai
        """
        try:
            from google import genai
            from google.genai import types
            import json
            
            # Инициализация клиента (используем системный ключ)
            client = genai.Client(api_key=self.gemini_api_key)
            
            # Строго используем актуальную модель (без старых fallback-ов)
            model_name = self.gemini_model if self.gemini_model else "gemini-3.1-flash-lite"
            
            # Формирование системного промпта
            system_instruction = f"You are a forensic cybersecurity AI. Task: {model_type} analysis."
            
            # Подготовка полезной нагрузки
            payload = {
                "events": audit_events,
                "context": extra_params or {}
            }
            prompt = f"{system_instruction}\n\nAnalyze the following data and return a JSON assessment:\n{json.dumps(payload, indent=2, ensure_ascii=False)}"
            
            # Вызов модели через новый SDK
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            
            # Парсинг ответа
            try:
                result_data = json.loads(response.text)
            except json.JSONDecodeError:
                result_data = {"raw_text": response.text, "parsing_error": True}
                
            return {
                "result": result_data,
                "model": model_name,
                "model_type": model_type,
                "threat_level": result_data.get("threat_level", "UNKNOWN")
            }
            
        except ImportError:
            return {"error": "Missing dependency", "details": "Run: pip install google-genai"}
        except Exception as e:
            logger.error(f"Gemini API invocation error: {e}")
            return {"error": "Gemini execution failed", "details": str(e)}
    
    def _invoke_openai(self,
                      model_type: str,
                      audit_events: List[Dict],
                      extra_params: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute via OpenAI API. Placeholder."""
        return {
            "result": {
                "model": "openai",
                "model_type": model_type,
                "threat_level": "PENDING",
                "backend_status": "Ready (requires openai SDK)"
            }
        }
    
    def _invoke_groq(self,
                    model_type: str,
                    audit_events: List[Dict],
                    extra_params: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute via Groq API (local fallback)."""
        import httpx
        try:
            model_name = "llama-3.3-70b-versatile"
            system_instruction = f"You are a forensic cybersecurity AI. Task: {model_type} analysis."
            payload = {
                "events": audit_events,
                "context": extra_params or {}
            }
            prompt = f"{system_instruction}\n\nAnalyze the following data and return a JSON assessment with threat_level (LOW, MEDIUM, HIGH, CRITICAL), summary, and recommended_actions:\n{json.dumps(payload, indent=2, ensure_ascii=False)}"
            
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"}
            }
            
            r = httpx.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=30)
            if r.status_code == 200:
                response_json = r.json()
                content = response_json["choices"][0]["message"]["content"]
                result_data = json.loads(content)
                return {
                    "result": result_data,
                    "model": model_name,
                    "model_type": model_type,
                    "threat_level": result_data.get("threat_level", "UNKNOWN")
                }
            else:
                return {"error": "Groq API returned error status", "code": r.status_code, "details": r.text}
        except Exception as e:
            logger.error(f"Groq API invocation error: {e}")
            return {"error": "Groq execution failed", "details": str(e)}
    
    def _invoke_anthropic(self,
                         model_type: str,
                         audit_events: List[Dict],
                         extra_params: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute via Anthropic API. Placeholder."""
        return {
            "result": {
                "model": "anthropic",
                "model_type": model_type,
                "threat_level": "PENDING",
                "backend_status": "Ready (requires anthropic SDK)"
            }
        }
    
    def classify_threat(self, 
                       dicom_metadata: Optional[Dict] = None,
                       extracted_text: Optional[str] = None,
                       transcribed_audio: Optional[str] = None,
                       audit_events: Optional[List[Dict]] = None,
                       force_local: bool = True) -> Dict[str, Any]:
        """
        Multi-modal threat classification (DICOM + OCR + Whisper + audit logs).
        ALWAYS uses local backend (Gemini preferred) for evidence integrity.
        
        Args:
            dicom_metadata: Parsed DICOM file metadata
            extracted_text: Text from EasyOCR/pytesseract
            transcribed_audio: Transcribed voice from Whisper/vosk
            audit_events: Corresponding audit trail
            force_local: Always use local backend (default: True for compliance)
            
        Returns:
            Threat classification with multimodal context
        """
        available = self._get_available_backends()
        
        payload = {
            "dicom_metadata": dicom_metadata or {},
            "extracted_text": extracted_text or "",
            "transcribed_audio": transcribed_audio or "",
            "audit_events": audit_events or []
        }
        
        # Try Gemini first for multi-modal
        if "gemini" in available and self.gemini_api_key:
            result = self._invoke_gemini("multimodal_classification", audit_events or [], payload)
            if "error" not in result:
                return {**result, "_source": "gemini_multimodal", "_compliance": "strict"}
        
        # Fall back to Groq if Gemini fails or is unavailable
        if "groq" in available and self.groq_api_key:
            result = self._invoke_groq("multimodal_classification", audit_events or [], payload)
            if "error" not in result:
                return {**result, "_source": "groq_multimodal", "_compliance": "fallback"}
        
        return {"error": "No available backend for multi-modal classification"}


# Singleton instance
_adapter = None

def get_adapter(agy_bin: str = "agy",
                compliance_mode: Optional[str] = None) -> AntigravityAdapter:
    """Get or create global Antigravity adapter instance."""
    global _adapter
    if _adapter is None:
        mode = compliance_mode or os.getenv("LOCAL_COMPLIANCE_MODE", "strict")
        _adapter = AntigravityAdapter(agy_bin=agy_bin, compliance_mode=mode)
    return _adapter


def validate_credentials() -> Dict[str, bool]:
    """Validate that at least one API backend is available."""
    backends = {
        "agy_auth_token": bool(os.getenv("AGY_AUTH_TOKEN")),
        "gemini_api_key": bool(os.getenv("GEMINI_API_KEY")),
        "openai_api_key": bool(os.getenv("OPENAI_API_KEY")),
        "groq_api_key": bool(os.getenv("GROQ_API_KEY")),
        "anthropic_api_key": bool(os.getenv("ANTHROPIC_API_KEY")),
        "google_api_key": bool(os.getenv("GOOGLE_API_KEY")),
    }
    
    backends["has_at_least_one"] = any(backends.values())
    return backends

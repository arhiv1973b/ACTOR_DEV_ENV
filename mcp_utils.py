import json, subprocess, os, logging

# Shared utilities for MCP server
TMP_OUT = r'H:\ACTOR_DEV_ENV\.native\out.json'
LOG_FILE = r'H:\ACTOR_DEV_ENV\.native\ps_error.log'

def run_ps(module_path, func, params):
    if os.path.exists(TMP_OUT): os.remove(TMP_OUT)
    if os.path.exists(LOG_FILE): os.remove(LOG_FILE)
    
    cmd = ["powershell", "-NoProfile", "-NonInteractive", "-File", r"H:\ACTOR_DEV_ENV\ps_wrapper.ps1",
           "-Module", module_path, "-Func", func, "-ParamsJson", json.dumps(params), "-OutFile", TMP_OUT]
    
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    
    # Always try to read the output JSON, even on error
    if os.path.exists(TMP_OUT):
        with open(TMP_OUT, 'r', encoding='utf-8-sig') as f: 
            output = json.load(f)
            if result.returncode == 0:
                return output
            return {"error": "PowerShell Script Failed", "details": output}

    if result.returncode != 0:
        return {"error": "PowerShell Script Failed", "details": result.stderr}
        
    return {"error": "No output file generated"}

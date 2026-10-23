import subprocess
import time
import json
import sys

models = [
    "qwen-forensic:latest",
    "qwen2.5:3b",
    "qwen2.5:7b",
    "llama3.1:8b",
    "gemma:2b",
    "deepseek-coder:1.3b",
    "qwen2.5:0.5b",
    "llama3.2:latest"
]

def handshake(model_name):
    print(f"--- Handshaking with {model_name} ---")
    prompt = "Say 'Handshake successful' and then provide a 1-sentence summary of your capabilities."
    
    start_time = time.time()
    try:
        # Using ollama run directly via subprocess
        process = subprocess.Popen(
            ["ollama", "run", model_name, prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(timeout=30)
        end_time = time.time()
        
        if process.returncode == 0:
            duration = end_time - start_time
            print(f"✅ Success! (Time: {duration:.2f}s)")
            print(f"Response: {stdout.strip()}")
            return duration
        else:
            print(f"❌ Failed: {stderr.strip()}")
            return None
    except subprocess.TimeoutExpired:
        print("❌ Failed: Timeout")
        return None
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        return None

if __name__ == "__main__":
    # Quick syntax check
    try:
        compile(open(__file__, 'r').read(), __file__, 'exec')
    except SyntaxError as e:
        print(f"🚨 SYNTAX ERROR DETECTED IMMEDIATELY: {e}")
        sys.exit(1)

    results = []
    for model in models:
        duration = handshake(model)
        if duration:
            results.append((model, duration))
    
    print("\n=== BENCHMARK RESULTS ===")
    if not results:
        print("No models responded.")
    else:
        # Sort by duration (ascending)
        results.sort(key=lambda x: x[1])
        for model, duration in results:
            print(f"{model:20} | {duration:.2f}s")

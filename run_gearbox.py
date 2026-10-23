import subprocess
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
    else:
        prompt = sys.stdin.read().strip()

    if not prompt:
        print("[Error] Передайте текст для анализа.")
        sys.exit(1)

    # Вызов чистого Gemini CLI
    result = subprocess.run(
        ["H:\\npm-global\\gemini.cmd", "--model", "gemini-3.1-flash-lite", "--prompt", prompt],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

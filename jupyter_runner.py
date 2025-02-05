# jupyter_runner.py

import subprocess
import sys

def start_jupyterlab(notebook_path: str = None, port: int = 8888):
    
    cmd = [
        "jupyter", "lab",
        "--no-browser",
        "--port", str(port),
    ]
    if notebook_path:
        cmd.append(notebook_path)

    print(f"[jupyter] Starting JupyterLab on port {port}")
    print(f"[jupyter] Notebook: {notebook_path if notebook_path else '(none)'}")

    try:
        proc = subprocess.Popen(cmd)
        return proc
    except FileNotFoundError:
        print("[jupyter] Error: 'jupyter' not found in your PATH.")
        sys.exit(1)
    except Exception as e:
        print(f"[jupyter] Failed to start JupyterLab: {e}")
        sys.exit(1)


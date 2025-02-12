# jupyter_runner.py

import subprocess
import threading
import sys
import os
import time
import re


def print_ssh_tunnel_instructions(port, token):
    print(f"""
[SSH Tunnel Instructions]
If this is a remote machine, on your laptop run:

  ssh -L {port}:localhost:{port} user@remote.yourdomain.edu

Then open in your local browser:

  http://localhost:{port}/?token={token}
""")

def monitor_stdout(stdout_file):
    with open(stdout_file, "r") as f:
        while True:
            line = f.readline()
            if "http://" in line or "https://" in line:
                url = line.strip()
                port_match = re.search(r':(\d+)/', url)
                port = port_match.group(1) if port_match else "N/A"
                token_match = re.search(r'token=([a-zA-Z0-9]+)', url)
                token = token_match.group(1) if token_match else "N/A"
                
                print(f"\n[jupyter] JupyterLab is running. Access it using the following URL:\n{url}")
                print(f"[jupyter] Token: {token}")
                print(f"[jupyter] Port: {port}")
                print_ssh_tunnel_instructions(port, token)
                break
            else:
                time.sleep(1)

def start_jupyterlab(notebook_path: str = None, port: int = 8888, run_dir: str = "/tmp"):
    
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
        stdout_file = os.path.join(run_dir, "jupyterlab.stdout")
        with open(stdout_file, "w") as stdout:
            proc = subprocess.Popen(
                cmd,
                stdout=stdout,
                stderr=stdout,
                text=True,
            )

            monitor_thread = threading.Thread(target=monitor_stdout, args=(stdout_file,))
            monitor_thread.start()

            return proc
    except FileNotFoundError:
        print("[jupyter] Error: 'jupyter' not found in your PATH.")
        sys.exit(1)
    except Exception as e:
        print(f"[jupyter] Failed to start JupyterLab: {e}")
        sys.exit(1)


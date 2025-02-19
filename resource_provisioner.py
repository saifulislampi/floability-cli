import subprocess
import sys
import os
import threading

def start_vine_factory(
    batch_type: str,
    manager_name: str,
    min_workers: int = 1,
    max_workers: int = 10,
    cores_per_worker: int = 1,
    poncho_env: str = None,
    scratch_dir: str = "/tmp/",
    run_dir: str = "/tmp/",
):
    cmd = [
        "vine_factory",
        f"-T{batch_type}",
        f"--scratch-dir={scratch_dir}",
        f"--manager-name={manager_name}",
        f"--min-workers={min_workers}",
        f"--max-workers={max_workers}",
        f"--cores={cores_per_worker}",
    ]
    
    if poncho_env:
        # from vine_factory help: --poncho-env=<file.tar.gz>
        cmd.append(f"--poncho-env={poncho_env}")

    print(f"[provision] Launching vine_factory: {' '.join(cmd)}")


    try:
        stdout_file = os.path.join(run_dir, "vine_factory.stdout")
        
        print(f"[provision] vine_factory stdout: {stdout_file}")

        with open(stdout_file, "w") as stdout:
            proc = subprocess.Popen(
                cmd,
                stdout=stdout,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid,
            )

            # stderr=stdout, #todo: parse this error for better error handling        
            def print_stderr(proc):
                for line in proc.stderr:
                    print(f"[provision] vine_factory error: {line.strip()}")

            # Start a thread to print stderr
            stderr_thread = threading.Thread(target=print_stderr, args=(proc,))
            stderr_thread.start()

            return proc
    except FileNotFoundError:
        print("[provision] Error: 'vine_factory' not found in PATH.")
        sys.exit(1)
    except Exception as e:
        print(f"[provision] Unexpected error launching vine_factory: {e}")
        sys.exit(1)

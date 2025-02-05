import subprocess
import sys

def start_vine_factory(
    batch_type: str,
    manager_name: str,
    min_workers: int = 1,
    max_workers: int = 10,
    cores_per_worker: int = 1,
    poncho_env: str = None,
    scratch_dir: str = "/tmp/"
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

    print(f"[factory] Launching vine_factory: {' '.join(cmd)}")


    try:
        proc = subprocess.Popen(cmd)
        return proc
    except FileNotFoundError:
        print("[factory] Error: 'vine_factory' not found in PATH.")
        sys.exit(1)
    except Exception as e:
        print(f"[factory] Unexpected error launching vine_factory: {e}")
        sys.exit(1)

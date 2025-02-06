#!/usr/bin/env python3
"""
floability-cli.py - Main entry point for Floability.

Example usage:
  python floability-cli.py \
      --environment environment.yml \
      --notebook my_notebook.ipynb \
      --batch-type condor \
      --workers 10 \
      --cores-per-worker 4 \
      --jupyter-port 9999
"""

import argparse
import time

from environment import create_conda_pack_from_yml
from provision import start_vine_factory
from cleanup import CleanupManager, install_signal_handlers
from jupyter_runner import start_jupyterlab


def print_ssh_tunnel_instructions(port: int):
    print(f"""
[SSH Tunnel Instructions]
If this is a remote machine, on your laptop run:

  ssh -L {port}:localhost:{port} user@remote.yourdomain.edu

Then open in your local browser:

  http://localhost:{port}
""")


def main():
    parser = argparse.ArgumentParser(
        description="Floability CLI: run distributed Jupyter-based workflows with TaskVine."
    )
    parser.add_argument("--environment", help="Path to environment.yml (optional).")
    parser.add_argument("--notebook", help="Path to a .ipynb file (optional).")

    parser.add_argument("--batch-type", default="condor",
                        choices=["local", "condor", "uge", "slurm"],
                        help="Batch system for vine_factory (default=condor).")
    parser.add_argument("--workers", type=int, default=5,
                        help="Number of workers for vine_factory (default=5).")
    parser.add_argument("--cores-per-worker", type=int, default=1,
                        help="Cores requested per worker (default=1).")
    parser.add_argument("--manager-name", default="floability-project",
                        help="TaskVine manager naem. Used for factory")

    parser.add_argument("--jupyter-port", type=int, default=8888,
                        help="Port on which JupyterLab will listen (default=8888).")

    args = parser.parse_args()

    # Initialize cleanup manager & install signal handlers
    cleanup_manager = CleanupManager()
    install_signal_handlers(cleanup_manager)

    # 1) Create conda-pack environment if provided
    poncho_env = None
    if args.environment:
        print(f"[floability] Creating conda-pack from '{args.environment}' using libmamba solver...")
        poncho_env = create_conda_pack_from_yml(
            env_yml=args.environment,
            output_file="floability_env.tar.gz",
            solver="libmamba",  # Hardcoded
            force=False         # Hardcoded
        )
    else:
        print("[floability] No environment file provided, skipping conda-pack.")

    # 2) Start vine_factory
    factory_proc = start_vine_factory(
        batch_type=args.batch_type,
        manager_name=args.manager_name,
        min_workers=1,
        max_workers=args.workers,
        cores_per_worker=args.cores_per_worker,
        poncho_env=poncho_env
    )
    cleanup_manager.register_subprocess(factory_proc)

    # 3) Always start Jupyter, even if --notebook not provided
    #    We'll pass None for the notebook_path if not given.
    jupyter_proc = start_jupyterlab(
        notebook_path=args.notebook,  # None if no notebook is specified
        port=args.jupyter_port
    )
    cleanup_manager.register_subprocess(jupyter_proc)

    print_ssh_tunnel_instructions(args.jupyter_port)

    # 4) Main loop
    print("[floability] Services running. Press Ctrl+C to stop (SIGINT to vine_factory).")

    try:
        while True:
            time.sleep(5)

            # Check if factory exited
            if factory_proc.poll() is not None:
                print("[floability] vine_factory ended.")
                break

            # Check if jupyter ended
            if jupyter_proc.poll() is not None:
                print("[floability] JupyterLab ended.")
                # Optionally break if you want the entire system to stop
                # break
    except KeyboardInterrupt:
        # The signal handler in cleanup.py typically handles this,
        # but if we get here, do a final fallback cleanup:
        print("[floability] KeyboardInterrupt in main loop. Cleaning up...")
        cleanup_manager.cleanup()

    print("[floability] Exiting main.")


if __name__ == "__main__":
    main()


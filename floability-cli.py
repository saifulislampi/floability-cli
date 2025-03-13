#!/usr/bin/env python3
"""
Floability CLI: main entry point for running distributed Jupyter-based workflows.
"""

import argparse
import time
import os
import subprocess
import uuid
from pathlib import Path

from environment import create_conda_pack_from_yml
from resource_provisioner import start_vine_factory
from cleanup import CleanupManager, install_signal_handlers
from jupyter_runner import start_jupyterlab
from utils import create_unique_directory, safe_extract_tar, update_manager_name_in_env
from data_handler import ensure_data_is_fetched


def get_parsed_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for the Floability CLI.
    """

    parser = argparse.ArgumentParser(
        description="Floability CLI: run distributed Jupyter-based workflows with TaskVine."
    )

    subparsers = parser.add_subparsers(dest="command", help="Floability sub-commands")

    # run sub-command
    run_parser = subparsers.add_parser(
        "run", help="Run a notebook or Floability backpack"
    )

    run_parser.add_argument(
        "--backpack",
        required=False,
        help="Path to the Floability backpack directory (optional).",
    )

    run_parser.add_argument(
        "--environment",
        help="Path to environment.yml or environment.tar.gz (optional).",
    )
    run_parser.add_argument("--notebook", help="Path to a .ipynb file (optional).")
    run_parser.add_argument(
        "--batch-type",
        default="local",
        choices=["local", "condor", "uge", "slurm"],
        help="Batch system for vine_factory (default=local).",
    )
    run_parser.add_argument(
        "--workers",
        type=int,
        default=5,
        help="Number of workers for vine_factory (default=5).",
    )
    run_parser.add_argument(
        "--cores-per-worker",
        type=int,
        default=1,
        help="Cores requested per worker (default=1).",
    )
    run_parser.add_argument(
        "--manager-name", help="TaskVine manager naem. Used for factory"
    )
    run_parser.add_argument(
        "--jupyter-port",
        type=int,
        default=8888,
        help="Port on which JupyterLab will listen (default=8888).",
    )
    run_parser.add_argument(
        "--base-dir",
        default="/tmp",
        help="Base directory for floability run directory files (default=/tmp).",
    )
    run_parser.add_argument(
        "--data-spec",
        help="Path to data.yml file specifying data to be fetched.",
    )
    run_parser.add_argument(
        "--backpack-root",
        default=".",
        help="Path to the root of the backpack (default='.').",
    )
    run_parser.add_argument(
        "--compute-spec",
        help="Path to compute.yml file specifying resource requirements.",
    )

    # fetch sub-command
    fetch_parser = subparsers.add_parser(
        "fetch", help="Fetch data from a data.yml spec"
    )
    fetch_parser.add_argument(
        "--data-spec",
        help="Path to data.yml file specifying data to be fetched.",
        required=True,
    )
    fetch_parser.add_argument(
        "--backpack-root",
        default=".",
        help="Path to the root of the backpack for 'backpack' source_type files (default='.')",
    )

    run_parser.add_argument(
        "--no-worker",
        action="store_true",
        help="Skip starting workers (optional).",
    )

    # pack sub-command
    pack_parser = subparsers.add_parser(
        "pack", help="Package a notebook into a Floability backpack"
    )

    # verify sub-command
    verify_parser = subparsers.add_parser("verify", help="Verify a Floability backpack")

    return parser.parse_args()


def resolve_backpack_args(args: argparse.Namespace) -> None:
    """
    Resolve the backpack arguments for the 'run' sub-command.
    """

    if not args.backpack:
        return

    backpack_dir = Path(args.backpack).resolve()
    backpack_name = str(backpack_dir.stem)

    print(f"Started processing backpack: {backpack_name}")

    if not backpack_dir.is_dir():
        print(
            f"Backpack directory not found: {backpack_dir}"
        )  # Todo: decide if we should raise an exception
        return

    if not args.data_spec:
        data_spec = backpack_dir / "data" / "data.yml"
        if data_spec.is_file():
            args.data_spec = str(data_spec)
            print(f"Using data spec from backpack: {args.data_spec}")

    if not args.compute_spec:
        compute_spec = backpack_dir / "compute" / "compute.yml"
        if compute_spec.is_file():
            args.compute_spec = str(compute_spec)
            print(f"Using compute spec from backpack: {args.compute_spec}")

    if not args.environment:
        env_path = backpack_dir / "software" / "environment.yml"
        # todo: add support for environment.tar.gz and other formats
        # todo: add support for other names

        if env_path.is_file():
            args.environment = str(env_path)
            print(f"Using environment from backpack: {args.environment}")

    if not args.notebook:
        workflow_dir = backpack_dir / "workflow"
        notebooks = list(workflow_dir.glob("*.ipynb"))

        if len(notebooks) == 1:
            args.notebook = str(notebooks[0])
            print(f"Using notebook from backpack: {args.notebook}")
        elif len(notebooks) > 1:  # take that has the same name as the backpack
            for notebook in notebooks:
                if notebook.stem == backpack_dir.stem:
                    args.notebook = str(notebook)
                    print(f"Using notebook from backpack: {args.notebook}")
                    break
        else:
            print(
                f"No notebook found in backpack: {workflow_dir}. Starting JupyterLab without a notebook."
            )

    args.backpack_root = str(backpack_dir)


def run_floability(args: argparse.Namespace, cleanup_manager: CleanupManager) -> None:
    """
    Main execution path for the 'run' sub-command.
    Orchestrates data fetching, environment creation/extraction, starting
    workers and JupyterLab, and manages cleanup.
    """
    resolve_backpack_args(args)

    run_dir = create_unique_directory(base_dir=args.base_dir, prefix="floability_run")

    print(
        f"[floability] Floability run directory: {run_dir}. All logs will be stored here."
    )

    # 1) Fetch data if data_spec is provided
    if args.data_spec:
        print(f"[floability] Fetching data from {args.data_spec}")
        ensure_data_is_fetched(args.data_spec, args.backpack_root)

    # Generate a unique manager name if none is provided
    if args.manager_name is None:
        args.manager_name = f"floability-{uuid.uuid4()}"

    print(f"[floability] Manager name: {args.manager_name}")

    poncho_env = None
    env_dir = None

    if args.environment:
        env_file_path = Path(args.environment)
        ext = Path(args.environment).suffix

        if ext in ["tar", "gz"]:
            poncho_env = str(env_file_path.resolve())
            print(f"[floability] Using conda-pack from '{args.environment}'")
        else:
            print(f"[floability] Creating conda-pack from '{args.environment}'")

            poncho_env = create_conda_pack_from_yml(
                env_yml=args.environment,
                solver="libmamba",
                force=False,
                base_dir=args.base_dir,
                run_dir=run_dir,
                manager_name=args.manager_name,
            )

        env_dir = os.path.join(run_dir, "current_conda_env")
        os.makedirs(env_dir, exist_ok=True)

        # 2a) Extract the environment
        try:
            safe_extract_tar(Path(poncho_env), Path(env_dir))
        except Exception as e:
            print(f"[floability] Error extracting environment: {e}")
            cleanup_manager.cleanup()
            return

        # 2b) Update the manager name in the environment
        update_manager_name_in_env(env_dir, args.manager_name)

        # 2c) Run conda-unpack.This fixes the path after extracting the environment
        try:
            subprocess.run(
                [
                    "conda",
                    "run",
                    "--prefix",
                    env_dir,
                    "--no-capture-output",
                    "conda-unpack",
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"[floability] Error running conda-unpack: {e}")
            cleanup_manager.cleanup()
            return

        cleanup_manager.register_directory(env_dir)

    else:
        print("[floability] No environment file provided, skipping conda-pack.")

    # 3) Start vine_factory
    if not args.no_worker:
        print("[floability] Starting vine_factory...")
        factory_proc = start_vine_factory(
            batch_type=args.batch_type,
            manager_name=args.manager_name,
            min_workers=1,
            max_workers=args.workers,
            cores_per_worker=args.cores_per_worker,
            poncho_env=poncho_env,
            run_dir=run_dir,
            scratch_dir=run_dir,
            config_yml=args.compute_spec,
        )
        cleanup_manager.register_subprocess(factory_proc)
    else:
        factory_proc = None
        print("[floability] vine_factory is disabled by --no-worker.")

    # 4) Always start Jupyter, even if --notebook not provided
    #    We'll pass None for the notebook_path if not given.
    print("[floability] Starting JupyterLab...")
    jupyter_proc = start_jupyterlab(
        notebook_path=args.notebook,  # None if no notebook is specified
        port=args.jupyter_port,
        run_dir=run_dir,
        conda_env_dir=env_dir,
    )
    cleanup_manager.register_subprocess(jupyter_proc)

    # 4) Main loop
    try:
        while True:
            time.sleep(5)

            # Check if factory exited
            if factory_proc is not None and factory_proc.poll() is not None:
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


def main():
    """
    Primary entry point for Floability CLI.
    """

    args = get_parsed_arguments()
    cleanup_manager = CleanupManager()
    install_signal_handlers(cleanup_manager)

    if args.command == "run":
        run_floability(args, cleanup_manager)
    elif args.command == "fetch":
        if not args.data_spec:
            print(
                "[floability] No data spec provided. Use --data-spec path/to/data.yml."
            )
            return
        ensure_data_is_fetched(args.data_spec, args.backpack_root)
    elif args.command == "pack":
        print("[floability] 'pack' command not yet implemented.")
    elif args.command == "verify":
        print("[floability] 'verify' command not yet implemented.")
    else:
        print("[floability] No command provided. Exiting.")


if __name__ == "__main__":
    main()

# environment.py
import os
import yaml        # pyyaml needed
import json
import shutil
import logging
import tempfile
import subprocess

from ndcctools.poncho import package_create


def create_conda_pack_from_yml(
    env_yml: str,
    output_file: str = "environment.tar.gz",
    solver: str = "libmamba",
    force: bool = False,
) -> str:
    
    if os.path.exists(output_file) and not force:
        print(f"[environment] '{output_file}' already exists. Use --force to overwrite.")
        return output_file

    temp_dir = tempfile.mkdtemp(prefix="conda_env_")
    env_path = os.path.join(temp_dir, "env")

    try:
        print(f"[environment] Creating env from '{env_yml}' with solver={solver}...")
        cmd_create = [
            "conda", "env", "create",
            "--file", env_yml,
            "--prefix", env_path,
            "--solver", solver
        ]
        subprocess.run(cmd_create, check=True)

        print(f"[environment] Packing environment into '{output_file}'...")
        cmd_pack = [
            "conda-pack",
            "-p", env_path,
            "-o", output_file,
            "--force"
        ]
        subprocess.run(cmd_pack, check=True)

        print(f"[environment] Environment successfully packed: {output_file}")

    except subprocess.CalledProcessError as e:
        print(f"[environment] Error creating or packing environment: {e}")
        raise
    finally:
        print(f"[environment] Cleaning up temporary directory: {temp_dir}")
        shutil.rmtree(temp_dir, ignore_errors=True)

    return output_file


def create_poncho_pack_from_env_yml(env_yml: str,
        cache: bool = True,
        cache_path: str = ".poncho_cache",
        force: bool = False) -> str:
    
    """Create a Poncho package from a Conda environment.yml file."""

    try:
        with open(env_yml, "r") as f:
            env_data = yaml.safe_load(f)

        poncho_spec = {"conda": {}, "pip": []}

        if "channels" in env_data:
            poncho_spec["conda"]["channels"] = env_data["channels"]

        conda_deps = []
        pip_deps = []

        deps = env_data.get("dependencies", [])
        for dep in deps:
            if isinstance(dep, dict) and "pip" in dep:
                pip_deps.extend(dep["pip"])
            else:
                conda_deps.append(dep)

        poncho_spec["conda"]["packages"] = conda_deps
        poncho_spec["pip"] = pip_deps
    
        print(poncho_spec)

        env_tarball = package_create.dict_to_env(
            poncho_spec,
            cache=cache,
            cache_path=cache_path,
            force=force
        )
        
        return env_tarball
        
    except Exception as e:
        raise 


import os
import time
import datetime
import getpass
import socket

SYSTEM_INFORMATION = None


def create_unique_directory(base_dir=".", prefix="floability_run", max_attempts=10):
    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            unique_dir = os.path.join(base_dir, f"{prefix}_{timestamp}")
            os.makedirs(unique_dir, exist_ok=False)

            return unique_dir

        except FileExistsError:
            print(f"Collision (unlikely) on attempt {attempt}. Retrying...")
            time.sleep(0.1)

        except OSError as e:
            print(f"OS Error on attempt {attempt}: {e}")
            raise

    raise RuntimeError(
        f"Failed to create a unique directory after {max_attempts} attempts."
    )


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connect to a public DNS server (Google)
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception as e:
        print(f"Error getting local IP: {e}")
        return None


def get_system_information():
    global SYSTEM_INFORMATION
    if SYSTEM_INFORMATION is None:
        SYSTEM_INFORMATION = {
            "username": getpass.getuser(),
            "hostname": socket.gethostname(),
            "ip_address": get_local_ip(),
        }

    return SYSTEM_INFORMATION

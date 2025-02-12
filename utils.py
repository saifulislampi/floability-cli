import os
import time
import datetime

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

    raise RuntimeError(f"Failed to create a unique directory after {max_attempts} attempts.")
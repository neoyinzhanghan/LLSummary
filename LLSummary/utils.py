import os
import pandas as pd
from tqdm import tqdm
import subprocess
import time


def rsync_with_retries(
    username, hostname, remote_result_dir, local_dir, max_retries=5, initial_backoff=1
):
    backoff = initial_backoff
    attempt = 0
    while attempt < max_retries:
        try:
            # Construct the rsync command
            remote_path = f"{username}@{hostname}:{remote_result_dir}/"
            command = ["rsync", "-avz", remote_path, local_dir]

            # Run the rsync command
            result = subprocess.run(command, check=True)

            if result.returncode == 0:
                print(f"Successfully synced {remote_result_dir} to {local_dir}")
                return True
        except subprocess.CalledProcessError as e:
            print(f"Error syncing {remote_result_dir}: {e}")
            attempt += 1
            print(f"Retrying in {backoff} seconds... (Attempt {attempt}/{max_retries})")
            time.sleep(backoff)
            backoff *= 2  # Exponential backoff

    print(f"Failed to sync {remote_result_dir} after {max_retries} attempts.")
    return False

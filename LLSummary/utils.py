import os
import pandas as pd
import time
import paramiko
import shutil
import io
import time
import stat
import subprocess
from contextlib import contextmanager
from tqdm import tqdm


@contextmanager
def ssh_open_file(
    username, hostname, remote_path, port=22, key_filename=None, password=None
):
    """
    Context manager to open a remote file over SSH and return a file-like object.

    Args:
        username (str): SSH username.
        hostname (str): Remote hostname or IP address.
        remote_path (str): Path to the file on the remote server.
        port (int): SSH port (default is 22).
        key_filename (str): Path to SSH private key file (optional).
        password (str): Password for SSH key (optional).

    Yields:
        file-like object: A file-like object for reading the remote file.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sftp = None
    remote_file = None

    try:
        if key_filename:
            client.connect(
                hostname, port=port, username=username, key_filename=key_filename
            )
        else:
            client.connect(hostname, port=port, username=username, password=password)

        sftp = client.open_sftp()
        remote_file = sftp.open(remote_path, mode="r")
        file_obj = io.StringIO(remote_file.read().decode("utf-8"))

        yield file_obj

    finally:
        if remote_file is not None:
            try:
                remote_file.close()
            except Exception as e:
                print(f"Error closing remote file: {e}")
        if sftp is not None:
            try:
                sftp.close()
            except Exception as e:
                print(f"Error closing SFTP connection: {e}")
        client.close()


def rsync_with_retries(
    username,
    hostname,
    remote_result_dir,
    local_dir,
    max_retries=5,
    initial_backoff=1,
    port=22,
    password=None,
    key_filename=None,
):
    backoff = initial_backoff
    attempt = 0

    if os.path.exists(local_dir):
        # Remove the local directory if it already exists
        shutil.rmtree(local_dir)

    os.makedirs(local_dir)

    while attempt < max_retries:
        try:
            # Construct the rsync command
            rsync_command = [
                "rsync",
                "-avz",  # Archive mode, verbose, compress
                "-e",
                f"ssh -p {port}",
                f"{username}@{hostname}:{remote_result_dir}/",  # Remote source
                local_dir,  # Local destination
            ]

            # Run the rsync command
            result = subprocess.run(rsync_command, check=True, capture_output=True)

            print(f"Successfully synced {remote_result_dir} to {local_dir}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"Error syncing {remote_result_dir}: {e.stderr.decode().strip()}")
            attempt += 1
            print(f"Retrying in {backoff} seconds... (Attempt {attempt}/{max_retries})")
            time.sleep(backoff)
            backoff *= 2  # Exponential backoff

    print(f"Failed to sync {remote_result_dir} after {max_retries} attempts.")
    return False


def scp_with_retries(
    username, hostname, cell_path, cell_save_path, max_retries=5, initial_backoff=1
):
    """
    Copies a file from a remote server to the local machine using SCP with retries and exponential backoff.

    :param username: Username for the remote server.
    :param hostname: Hostname or IP address of the remote server.
    :param cell_path: Path to the file on the remote server.
    :param cell_save_path: Path to save the file locally.
    :param max_retries: Maximum number of retry attempts.
    :param initial_backoff: Initial backoff time in seconds.
    :return: True if the file is successfully copied, False otherwise.
    """
    backoff = initial_backoff
    attempt = 0

    while attempt < max_retries:
        try:
            # Construct the SCP command
            remote_path = f"{username}@{hostname}:{cell_path}"
            cell_filename = os.path.basename(cell_path)
            # separate the directory and the file name
            cell_save_dir = os.path.dirname(cell_save_path)

            os.makedirs(cell_save_dir, exist_ok=True)
            command = ["scp", remote_path, cell_save_dir]

            current_name = os.path.join(cell_save_dir, cell_filename)
            os.rename(current_name, cell_save_path)

            # Run the SCP command
            result = subprocess.run(command, check=True)

            if result.returncode == 0:
                print(f"Successfully copied {cell_path} to {cell_save_path}")
                return True
        except subprocess.CalledProcessError as e:
            print(f"Error copying {cell_path}: {e}")
            attempt += 1
            print(f"Retrying in {backoff} seconds... (Attempt {attempt}/{max_retries})")
            time.sleep(backoff)
            backoff *= 2  # Exponential backoff

    print(f"Failed to copy {cell_path} after {max_retries} attempts.")
    return False

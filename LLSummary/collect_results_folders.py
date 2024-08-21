import os
import pandas as pd
import shutil
from tqdm import tqdm
from LLSummary.utils import rsync_with_retries
from LLRunner.config import results_dir


def collect_result_folders(cohort_files, save_dir):
    os.makedirs(save_dir, exist_ok=True)

    metadata_dict = {
        "cohort_file": [],
        "wsi_name": [],
        "username": [],
        "hostname": [],
        "machine": [],
        "remote_result_dir": [],
        "Dx": [],
        "sub_Dx": [],
        "datetime_processed": [],
        "note": [],
    }

    for cohort_file in cohort_files:
        print(f"Copying result folders for cohort file {cohort_file}.")

        df = pd.read_csv(cohort_file)

        # Iterate over rows using tqdm
        for i, row in tqdm(df.iterrows(), total=df.shape[0]):
            username = row["username"]
            hostname = row["hostname"]
            remote_result_dir = row["remote_result_dir"]
            remote_result_dir = os.path.join(results_dir, remote_result_dir)

            # Define the local directory to save the data
            local_dir = os.path.join(save_dir, os.path.basename(remote_result_dir))

            # Remove the local directory if it already exists, to always overwrite the data
            if os.path.exists(local_dir):
                shutil.rmtree(local_dir)

            os.makedirs(local_dir, exist_ok=True)

            # Run the rsync command with retries and exponential backoff
            rsync_with_retries(
                username,
                hostname,
                remote_result_dir,
                local_dir,
                max_retries=5,
                initial_backoff=1,
            )

            # Add metadata to the metadata_dict
            metadata_dict["cohort_file"].append(cohort_file)
            metadata_dict["wsi_name"].append(row["wsi_name"])
            metadata_dict["username"].append(username)
            metadata_dict["hostname"].append(hostname)
            metadata_dict["machine"].append(row["machine"])
            metadata_dict["remote_result_dir"].append(row["remote_result_dir"])
            metadata_dict["Dx"].append(row["Dx"])
            metadata_dict["sub_Dx"].append(row["sub_Dx"])
            metadata_dict["datetime_processed"].append(row["datetime_processed"])
            metadata_dict["note"].append(row["note"])

    # Save the metadata_dict as a DataFrame
    metadata_df = pd.DataFrame(metadata_dict)

    # Save the metadata_df as a CSV file
    metadata_df.to_csv(os.path.join(save_dir, "metadata.csv"), index=False)


if __name__ == "__main__":

    pass

    # Example usage:
    # cohort_files = ["/media/hdd3/greg/AML_bma.csv"]
    # save_dir = "/media/hdd3/greg/test"
    # process_cohort_files(cohort_files, save_dir)

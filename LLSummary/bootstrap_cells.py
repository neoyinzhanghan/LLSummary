import os
import pandas as pd
from tqdm import tqdm
from LLSummary.utils import rsync_with_retries, scp_with_retries, ssh_open_file
from LLRunner.config import results_dir

cohort_files = []
save_dir = "/media/hdd3/greg/test"

num_cartridges = 10

metadata_dicts = []
cell_names = [
    "B1",
    "B2",
    "E1",
    "E4",
    "ER1",
    "ER2",
    "ER3",
    "ER4",
    "ER5",
    "ER6",
    "L2",
    "L4",
    "M1",
    "M2",
    "M3",
    "M4",
    "M5",
    "M6",
    "MO2",
    "PL2",
    "PL3",
    "U1",
]


for i in range(num_cartridges):
    # make a directory for the cartridge in the save_dir
    cartridge_dir = os.path.join(save_dir, f"cartridge_{i}")

    os.makedirs(cartridge_dir, exist_ok=True)

    metadata_dict = {
        "cell_id": [],
        "wsi_name": [],
        "username": [],
        "hostname": [],
        "machine": [],
        "remote_result_dir": [],
        "original_name": [],
        "Dx": [],
        "sub_Dx": [],
        "confidence": [],
        "note": [],
        "datetime_processed": [],
        "label": [],
        "VoL": [],
    }

    for cellname in cell_names:
        metadata_dict[cellname] = []

    metadata_dicts.append(metadata_dict)

# make a directory for the cartridge in the save_dir
cartridge_dir = os.path.join(save_dir, f"cartridge_{i}")

metadata_dict = {}

cell_id = 0

for cohort_file in cohort_files:

    # Load the cohort file
    df = pd.read_csv(cohort_file)

    # Iterate over rows using tqdm
    for i, row in tqdm(df.iterrows(), total=df.shape[0]):
        remote_result_dir = row["remote_result_dir"]
        remote_result_dir = os.path.join(results_dir, remote_result_dir)
        username, hostname = row["username"], row["hostname"]

        # Define the remote file path
        cells_info_file = os.path.join(remote_result_dir, "cells", "cells_info.csv")

        # Read the remote csv file using ssh_open_file (Assuming ssh_open_file reads the file from the remote system)
        with ssh_open_file(username, hostname, cells_info_file) as f:
            cells_info_df = pd.read_csv(f)

        # randomly sample num_cartridges number of cells with replacement
        sampled_cells_info_df = cells_info_df.sample(n=num_cartridges, replace=True)

        # iterate over the sampled cells
        for i in range(num_cartridges):
            # get the row of the sampled cell df as dict
            cell_info = sampled_cells_info_df.iloc[i].to_dict()

            # get the name of the cell
            name = cell_info["name"]
            label = cell_info["label"]

            # cell_path is remote_result_dir/cells/label/name
            cell_path = os.path.join(remote_result_dir, "cells", label, name)

            # define the local directory to save the data
            cartridge_dir = os.path.join(save_dir, f"cartridge_{i}")
            cell_dir = os.path.join(cartridge_dir, label)
            cell_save_path = os.path.join(cell_dir, f"{cell_id}.jpg")

            # scp the cell_path to the cell_save_path
            scp_with_retries(username, hostname, cell_path, cell_save_path)

            # add metadata to the metadata_dict
            metadata_dicts[i]["cell_id"].append(cell_id)
            metadata_dicts[i]["wsi_name"].append(row["wsi_name"])
            metadata_dicts[i]["username"].append(username)
            metadata_dicts[i]["hostname"].append(hostname)
            metadata_dicts[i]["machine"].append(row["machine"])
            metadata_dicts[i]["remote_result_dir"].append(row["remote_result_dir"])
            metadata_dicts[i]["original_name"].append(name)
            metadata_dicts[i]["Dx"].append(row["Dx"])
            metadata_dicts[i]["sub_Dx"].append(row["sub_Dx"])
            metadata_dicts[i]["confidence"].append(row["confidence"])
            metadata_dicts[i]["note"].append(row["note"])
            metadata_dicts[i]["datetime_processed"].append(row["datetime_processed"])
            metadata_dicts[i]["label"].append(label)
            metadata_dicts[i]["VoL"].append(cell_info["VoL"])

            for cellname in cell_names:
                metadata_dicts[i][cellname].append(cell_info[cellname])

            cell_id += 1

# save the metadata_dicts as a list of DataFrames
metadata_dfs = [pd.DataFrame(metadata_dict) for metadata_dict in metadata_dicts]

# save the metadata_dfs as CSV files
for i, metadata_df in enumerate(metadata_dfs):
    metadata_df.to_csv(
        os.path.join(save_dir, f"cartridge_{i}", "metadata.csv"), index=False
    )

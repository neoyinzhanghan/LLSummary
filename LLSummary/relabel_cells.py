import os
import pandas as pd
from tqdm import tqdm

selected_results_dir = "LLSummary/LLSummary_2021-06-30"
save_dir = "LLSummary/LLSummary_2021-06-30_relabel"

cellnames = [
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
    "U4",
]


relabelling_metadata = {
    "original_cell_path": [],
    "original_label": [],
    "new_cell_path": [],
    "new_label": [],
}

# first get all the subdirectories of selected_results_dir
dirs_lst = [
    d
    for d in os.listdir(selected_results_dir)
    if os.path.isdir(os.path.join(selected_results_dir, d))
]

# check the it is a dir and that is has a cells further subdirectory and it does not contain a file named error.txt
dirs_lst = [
    d
    for d in dirs_lst
    if os.path.isdir(os.path.join(selected_results_dir, d, "cells"))
    and not os.path.exists(os.path.join(selected_results_dir, d, "error.txt"))
]

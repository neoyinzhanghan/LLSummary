from LLRunner.config import available_machines
from LLRunner.slide_result_compiling.compile_results import compile_results
import pandas as pd


def _parse_output_string(output_string):
    """Parse the output_string"""
    pipeline_datetime_processed, wsi_name, machine = output_string.split("<<<")
    pipeline, datetime = pipeline_datetime_processed.split("_")
    remote_result_folder = pipeline_datetime_processed

    return remote_result_folder, pipeline, datetime, wsi_name, machine


def _parse_output_list(output_list):
    """Parse the output_list"""
    df_dct = {
        "pipeline": [],
        "datetime_processed": [],
        "wsi_name": [],
        "machine": [],
        "remote_result_folder": [],
    }

    for output_string in output_list:
        remote_result_folder, pipeline, datetime, wsi_name, machine = (
            _parse_output_string(output_string)
        )
        df_dct["pipeline"].append(pipeline)
        df_dct["datetime_processed"].append(datetime)
        df_dct["wsi_name"].append(wsi_name)
        df_dct["machine"].append(machine)
        df_dct["remote_result_folder"].append(remote_result_folder)

    return df_dct


def parse_list_of_output_list(output_list_list):
    """Parse the output_dict_list"""

    df_dct = {
        "pipeline": [],
        "datetime_processed": [],
        "wsi_name": [],
        "machine": [],
        "remote_result_folder": [],
    }

    for output_list in output_list_list:
        df_dct_tmp = _parse_output_list(output_list)
        # use extend instead of append to avoid nested lists
        df_dct["pipeline"].extend(df_dct_tmp["pipeline"])
        df_dct["datetime_processed"].extend(df_dct_tmp["datetime_processed"])
        df_dct["wsi_name"].extend(df_dct_tmp["wsi_name"])
        df_dct["machine"].extend(df_dct_tmp["machine"])
        df_dct["remote_result_folder"].extend(df_dct_tmp["remote_result_folder"])

    return pd.DataFrame(df_dct)


def find_tmp_df_rows(output_list_list):
    """Parse the output_list_list and then find the rows in tmp_df that match the parsed results"""
    tmp_df = compile_results()
    output_df = parse_list_of_output_list(output_list_list)
    # get the list of unique wsi_names in the output_df
    wsi_names = output_df["wsi_name"].unique()
    # filter the rowss in tmp_df that have wsi_name in the wsi_names list
    filtered_df = tmp_df[tmp_df["wsi_name"].isin(wsi_names)]

    return filtered_df

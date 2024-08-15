from LLRunner.config import available_machines
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

from LLSummary.parsing import parse_list_of_output_list
from LLRunner.slide_result_compiling.compile_results import compile_results
import pandas as pd

tmp_df = compile_results()
tmp_df["datetime_processed"] = pd.to_datetime(tmp_df["datetime_processed"])

output_list = []

output_df = parse_list_of_output_list(output_list)


# get the list of unique wsi_names in the output_df
wsi_names = output_df["wsi_name"].unique()

print(wsi_names[:5])

# filter the rowss in tmp_df that have wsi_name in the wsi_names list
filtered_df = tmp_df[tmp_df["wsi_name"].isin(wsi_names)]

# print the number of rows ins the filtered_df
print(filtered_df.shape[0])

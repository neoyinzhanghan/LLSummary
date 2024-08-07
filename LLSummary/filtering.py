
#####
# The tmp_df has the following columns:
# - 'machine': the slide id
# - 'hostname': the hostname of the machine
# - 'username': the username of the machine
# - 'remote_result_dir': the remote directory where the results are stored
# - 'wsi_name': the name of the slide
# - 'pipeline': the pipeline used to generate the results
# - 'Dx': the diagnosis of the slide
# - 'sub_Dx': the sub-diagnosis of the slide
# - 'datetime_processed': the date and time the slide was processed
# - 'note': any notes about the slide
#####

import streamlit as st
import pandas as pd
# Assuming tmp_df is generated from compile_results
from LLRunner.slide_result_compilation.compile_results import compile_results

tmp_df = compile_results()

# Title of the app
st.title("Slide Result Selector")

# Filter options
st.sidebar.header("Filter Options")

# Filter by machine
machine_options = tmp_df['machine'].unique()
selected_machine = st.sidebar.multiselect("Select Machine", machine_options, default=machine_options)

# Filter by pipeline
pipeline_options = tmp_df['pipeline'].unique()
selected_pipeline = st.sidebar.multiselect("Select Pipeline", pipeline_options, default=pipeline_options)

# Filter by Dx
dx_options = tmp_df['Dx'].unique()
selected_dx = st.sidebar.multiselect("Select Dx", dx_options, default=dx_options)

# Filter by sub_Dx
sub_dx_options = tmp_df['sub_Dx'].unique()
selected_sub_dx = st.sidebar.multiselect("Select Sub Dx", sub_dx_options, default=sub_dx_options)

# Filter by note
note_options = tmp_df['note'].unique()
selected_note = st.sidebar.multiselect("Select Note", note_options, default=note_options)

# Filter by datetime_processed
min_date = tmp_df['datetime_processed'].min()
max_date = tmp_df['datetime_processed'].max()
selected_dates = st.sidebar.slider("Select Date Range", min_value=min_date, max_value=max_date, value=(min_date, max_date))

# Filter the DataFrame
filtered_df = tmp_df[
    (tmp_df['machine'].isin(selected_machine)) &
    (tmp_df['pipeline'].isin(selected_pipeline)) &
    (tmp_df['Dx'].isin(selected_dx)) &
    (tmp_df['sub_Dx'].isin(selected_sub_dx)) &
    (tmp_df['note'].isin(selected_note)) &
    (tmp_df['datetime_processed'].between(selected_dates[0], selected_dates[1]))
]

# Generate options for the multiselect based on the filtered DataFrame
options = filtered_df.apply(
    lambda row: f"{row['pipeline']}_{row['datetime_processed']}<<<{row['wsi_name']}", axis=1
).tolist()

# Multiselect for slides
selected_slides = st.multiselect("Select Slides", options, default=options)

# Display the selected slides
if selected_slides:
    st.write("Selected Slides:")
    st.write(selected_slides)
else:
    st.write("No slides selected.")

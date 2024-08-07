
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
from LLRunner.slide_result_compiling.compile_results import compile_results

# Generate the DataFrame from compile_results
tmp_df = compile_results()

# Convert 'datetime_processed' to datetime if it's not already
tmp_df['datetime_processed'] = pd.to_datetime(tmp_df['datetime_processed'])

# Title of the app
st.title("Slide Result Selector")

# Sidebar for filter options
st.sidebar.header("Filter Options")

# Filter by machine
machine_options = tmp_df['machine'].unique()
selected_machine = st.sidebar.multiselect("Select Machine", machine_options)

# Filter by pipeline
pipeline_options = tmp_df['pipeline'].unique()
selected_pipeline = st.sidebar.multiselect("Select Pipeline", pipeline_options)

# Filter by Dx (Diagnosis)
dx_options = tmp_df['Dx'].unique()
selected_dx = st.sidebar.multiselect("Select Dx", dx_options)

# Conditional sub_Dx filter based on selected Dx
if selected_dx:
    sub_dx_options = tmp_df[tmp_df['Dx'].isin(selected_dx)]['sub_Dx'].unique()
    selected_sub_dx = st.sidebar.multiselect("Select Sub Dx", sub_dx_options)
else:
    selected_sub_dx = []

# Filter by note (Subtractive: if no note is selected, no filter is applied)
note_options = tmp_df['note'].unique()
selected_note = st.sidebar.multiselect("Select Note", note_options)

# Filter by datetime_processed using a date range slider
min_date = tmp_df['datetime_processed'].min().to_pydatetime()
max_date = tmp_df['datetime_processed'].max().to_pydatetime()
selected_dates = st.sidebar.slider(
    "Select Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)
)

# Add an "Apply Filters" button
if st.sidebar.button("Apply Filters"):
    # Filter the DataFrame based on selections
    filtered_df = tmp_df.copy()

    if selected_machine:
        filtered_df = filtered_df[filtered_df['machine'].isin(selected_machine)]
    if selected_pipeline:
        filtered_df = filtered_df[filtered_df['pipeline'].isin(selected_pipeline)]
    if selected_dx:
        filtered_df = filtered_df[filtered_df['Dx'].isin(selected_dx)]
    if selected_sub_dx:
        filtered_df = filtered_df[filtered_df['sub_Dx'].isin(selected_sub_dx)]
    if selected_note:
        filtered_df = filtered_df[filtered_df['note'].isin(selected_note)]
    filtered_df = filtered_df[
        filtered_df['datetime_processed'].between(selected_dates[0], selected_dates[1])
    ]

    # Generate options for the multiselect based on the filtered DataFrame
    options = filtered_df.apply(
        lambda row: f"{row['pipeline']}_{row['datetime_processed']}<<<{row['wsi_name']}",
        axis=1
    ).tolist()

    # Add a "Select All" button for slides
    if st.button("Select All Slides"):
        selected_slides = options
    else:
        selected_slides = st.multiselect("Select Slides", options, default=options)

    # Display the selected slides
    if selected_slides:
        st.write("Selected Slides:")
        st.write(selected_slides)
    else:
        st.write("No slides selected.")

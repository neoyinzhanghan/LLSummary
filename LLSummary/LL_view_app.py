import os
import streamlit as st
import pandas as pd
from PIL import Image
from LLRunner.slide_result_compiling.compile_results import compile_results
from LLSummary.config import result_cards_dir
from LLSummary.result_cards import find_result_card


def generate_label(row):
    idx = row.name  # Use the DataFrame index as the idx
    machine = row["machine"]  # Shorten machine to the first 5 characters
    pipeline_short = row["pipeline"]  # Shorten pipeline to the first 5 characters
    wsi = row["wsi_name"]
    return f"[{idx}] {pipeline_short}_{row['datetime_processed'].strftime('%Y-%m-%d %H:%M:%S')}<<<{wsi}<<<{machine}"


@st.cache_data
def load_data():
    """Load and cache the results data."""
    tmp_df = compile_results()
    tmp_df["datetime_processed"] = pd.to_datetime(tmp_df["datetime_processed"])

    # Generate the labels with indices based on the DataFrame index
    tmp_df["label"] = tmp_df.apply(generate_label, axis=1)
    return tmp_df


# Generate the DataFrame from compile_results (cached)
tmp_df = load_data()

# Title of the app
st.title("Slide Result Selector")

# Sidebar for filter options
st.sidebar.header("Filter Options")

# Filter by machine
machine_options = tmp_df["machine"].unique()
selected_machine = st.sidebar.multiselect("Select Machine", machine_options)

# Filter by pipeline
pipeline_options = tmp_df["pipeline"].unique()
selected_pipeline = st.sidebar.multiselect("Select Pipeline", pipeline_options)

# Filter by Dx (Diagnosis)
dx_options = tmp_df["Dx"].unique()
selected_dx = st.sidebar.multiselect("Select Dx", dx_options)

# Conditional sub_Dx filter based on selected Dx
if selected_dx:
    sub_dx_options = tmp_df[tmp_df["Dx"].isin(selected_dx)]["sub_Dx"].unique()
    selected_sub_dx = st.sidebar.multiselect("Select Sub Dx", sub_dx_options)
else:
    selected_sub_dx = []

# Filter by note (Subtractive: if no note is selected, no filter is applied)
note_options = tmp_df["note"].unique()
selected_note = st.sidebar.multiselect("Select Note", note_options)

# Filter by datetime_processed using a date range slider
min_date = tmp_df["datetime_processed"].min().to_pydatetime()
max_date = tmp_df["datetime_processed"].max().to_pydatetime()
selected_dates = st.sidebar.slider(
    "Select Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
)

# Add a checkbox to toggle the display of result cards
show_result_cards = st.sidebar.checkbox("Show Result Cards", value=True)

# Add an "Apply Filters" button
if st.sidebar.button("Apply Filters"):
    # Filter the DataFrame based on selections
    filtered_df = tmp_df.copy()

    if selected_machine:
        filtered_df = filtered_df[filtered_df["machine"].isin(selected_machine)]
    if selected_pipeline:
        filtered_df = filtered_df[filtered_df["pipeline"].isin(selected_pipeline)]
    if selected_dx:
        filtered_df = filtered_df[filtered_df["Dx"].isin(selected_dx)]
    if selected_sub_dx:
        filtered_df = filtered_df[filtered_df["sub_Dx"].isin(selected_sub_dx)]
    if selected_note:
        filtered_df = filtered_df[filtered_df["note"].isin(selected_note)]
    filtered_df = filtered_df[
        filtered_df["datetime_processed"].between(selected_dates[0], selected_dates[1])
    ]

    # Store the filtered labels and options in session state
    st.session_state["labels"] = filtered_df["label"].tolist()
    st.session_state["original_options"] = filtered_df.apply(
        lambda row: generate_label(row), axis=1
    ).tolist()

# Retrieve the labels from session state
labels = st.session_state.get("labels", [])
original_options = st.session_state.get("original_options", [])

# Handle the "Select All" functionality
if st.button("Select All Slides"):
    st.session_state["selected_slides"] = original_options

# Maintain multiselect with current state
selected_slides = st.session_state.get("selected_slides", [])
selected_slides_display = st.multiselect(
    "Select Slides",
    labels,
    default=[labels[original_options.index(slide)] for slide in selected_slides],
)

# Update session state with the current selections
st.session_state["selected_slides"] = [
    original_options[labels.index(display)] for display in selected_slides_display
]

# Display the selected slides with labels
if st.session_state["selected_slides"]:
    st.write("Selected Slides:")
    # st.write(st.session_state["selected_slides"])

    # Conditionally display the result cards based on the checkbox
    if show_result_cards:
        st.write("Result Cards:")
        cols = st.columns(4)  # Create 4 columns for the image grid

        for i, slide in enumerate(st.session_state["selected_slides"]):
            with cols[i % 4]:  # Place each image in a column
                # Extract the remote_result_dir from the slide string
                pipeline_datetime_processed, wsi_name, _ = slide.split("]")[1].strip().split("<<<")
                datetime_processed = pipeline_datetime_processed.split("_")[1]
                remote_result_dir = slide.split("]")[1].strip().split("<<<")[0]

                # Find and display the result card
                image_path = find_result_card(remote_result_dir)

                if image_path:
                    image = Image.open(image_path)
                    label = tmp_df.loc[
                        tmp_df["remote_result_dir"] == pipeline_datetime_processed, "label"
                    ].values[0]
                    st.image(
                        image, caption=label, use_column_width=True
                    )  # Display the full image with the pseudo-index as caption
    else:
        st.write("Result cards display is turned off.")
else:
    st.write("No slides selected.")

# Display a submit button and an input box for saving the filtered DataFrame
dir_input = st.text_input("Specify the path to save the file in the format of /path/to/file/filename.csv:")

if st.button("Submit"):
    if dir_input and selected_slides_display:
        # Extract the indices from the original DataFrame
        indices = [int(slide.split(']')[0].strip('[')) for slide in selected_slides_display]
        # Filter the DataFrame to only include selected slides
        save_df = tmp_df.loc[indices, :]
        # Construct the file path
        file_path = dir_input
        # Save the DataFrame as a CSV file
        save_df.to_csv(file_path, index=False)
        st.success(f"File saved successfully at {file_path}")
    else:
        st.error("Please specify a valid directory and ensure slides are selected.")

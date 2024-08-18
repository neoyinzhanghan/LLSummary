import os
import streamlit as st
from LLSummary.sample_cells_by_classes import (
    sample_cells_by_classes,
)  # Import the function from your module


def main():
    st.title("Data Processing App")

    # User selects what they want to do
    option = st.selectbox(
        "Select the action you want to perform:",
        options=[
            "Sample Cells by Classes",
        ],
    )

    if option == "Sample Cells by Classes":
        st.subheader("Sample Cells by Classes")

        # Collecting user inputs
        cohort_files_input = st.text_area(
            "Enter the cohort files paths (comma-separated):"
        )
        cohort_files = [file.strip() for file in cohort_files_input.split(",")]

        save_dir = st.text_input("Enter the save directory path:")

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

        cell_types = st.multiselect(
            "Select cell types to include (based on cell names):", cell_names
        )

        num_cartridges = st.number_input(
            "Enter the number of cartridges:", min_value=1, value=10
        )

        num_per_cartridge = st.number_input(
            "Enter the number of samples per cartridge:", min_value=1, value=3
        )

        # Button to submit and run the processing
        if st.button("Process Files"):

            # if the save_dir does not exist, create it
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            else:
                st.warning(
                    "The save directory already exists. Files may be overwritten."
                )
                # ask the user if they want to overwrite the files
                overwrite = st.checkbox("Overwrite existing files?")

            with st.spinner("Processing... see console for details"):
                sample_cells_by_classes(
                    cohort_files,
                    save_dir,
                    cell_types,
                    num_cartridges,
                    num_per_cartridge,
                    cell_names,
                )
            st.success("Processing completed!")


if __name__ == "__main__":
    main()

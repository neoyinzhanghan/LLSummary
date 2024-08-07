import os
from tqdm import tqdm
from LLRunner.slide_result_compiling.BMA_diff_result_card import get_mini_result_card
from LLSummary.config import result_cards_dir

def create_result_cards(tmp_df):
    """ Create result cards for each slide in the filtered DataFrame. """

    # if the result_cards_dir doesn't exist, create it
    if not os.path.exists(result_cards_dir):
        os.makedirs(result_cards_dir)

    # Iterate over rows of the tmp_df
    for index, row in tqdm(tmp_df.iterrows(), total=tmp_df.shape[0], desc="Creating Result Cards"):
        # Get the mini result card        
        remote_result_dir = row['remote_result_dir']
        machine = row['machine']

        image_file_name = remote_result_dir + "_result_card.png"

        image_file_path = os.path.join(result_cards_dir, image_file_name)

        # if the image file doesn't exist, create it
        if not os.path.exists(image_file_path):
            mini_result_card = get_mini_result_card(remote_result_dir, machine)
            mini_result_card.save(image_file_path)

def find_result_card(remote_result_dir):
    """ Find the result card for a given remote_result_dir. """
    
    image_file_name = remote_result_dir + "_result_card.png"
    image_file_path = os.path.join(result_cards_dir, image_file_name)

    # if the image file exists, return the path
    if os.path.exists(image_file_path):
        return image_file_path
    else:
        return None
    
if __name__ == "__main__":
    import pandas as pd
    from LLRunner.slide_result_compiling.compile_results import compile_results
    # Generate the DataFrame from compile_results
    tmp_df = compile_results()

    # Convert 'datetime_processed' to datetime if it's not already
    tmp_df['datetime_processed'] = pd.to_datetime(tmp_df['datetime_processed'])

    create_result_cards(tmp_df)
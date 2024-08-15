import os
import ray
import time
import random
from tqdm import tqdm
from LLRunner.slide_result_compiling.BMA_diff_result_card import get_mini_result_card
from LLRunner.config import results_dir
from LLSummary.config import result_cards_dir


@ray.remote
def process_single_card(
    row,
    result_cards_dir=result_cards_dir,
    results_dir=results_dir,
    max_retries=7,
    backoff_factor=1.5,
):
    """Process a single result card with retry logic."""
    remote_result_dir = row["remote_result_dir"]
    machine = row["machine"]

    image_file_name = remote_result_dir + "_result_card.png"
    image_file_path = os.path.join(result_cards_dir, image_file_name)

    retries = 0
    while retries < max_retries:
        try:
            # If the image file doesn't exist, create it
            if not os.path.exists(image_file_path):
                mini_result_card = get_mini_result_card(
                    os.path.join(results_dir, remote_result_dir), machine
                )
                mini_result_card.save(image_file_path)
            else:
                print(
                    f"Skipping {remote_result_dir} on {machine}: Result card already exists."
                )
            break  # Exit loop if successful
        except Exception as e:
            retries += 1
            wait_time = backoff_factor**retries + random.uniform(
                0, 1
            )  # Exponential backoff with jitter
            print(
                f"Error processing {remote_result_dir} on {machine}: {e}. Retrying {retries}/{max_retries} in {wait_time:.2f} seconds."
            )
            time.sleep(wait_time)
    else:
        print(
            f"Failed to process {remote_result_dir} on {machine} after {max_retries} retries."
        )


def create_result_cards(
    tmp_df,
    result_cards_dir=result_cards_dir,
    results_dir=results_dir,
    max_concurrency=10,
):
    """Create result cards for each slide in the filtered DataFrame with limited concurrency."""

    # if the result_cards_dir doesn't exist, create it
    if not os.path.exists(result_cards_dir):
        os.makedirs(result_cards_dir)

    # Launch tasks in parallel with controlled concurrency
    futures = []
    with tqdm(total=len(tmp_df), desc="Creating Result Cards") as pbar:
        for index, row in tmp_df.iterrows():
            if len(futures) >= max_concurrency:
                # Wait for at least one task to complete before launching a new one
                done, futures = ray.wait(futures, num_returns=1)
                pbar.update(len(done))

            # Start a new task
            futures.append(
                process_single_card.remote(row, result_cards_dir, results_dir)
            )

        # Wait for the remaining tasks to complete
        while futures:
            done, futures = ray.wait(futures, num_returns=1)
            pbar.update(len(done))

    # Ensure all tasks are completed
    ray.get(futures)


# def create_result_cards(tmp_df):
#     """ Create result cards for each slide in the filtered DataFrame. """

#     # if the result_cards_dir doesn't exist, create it
#     if not os.path.exists(result_cards_dir):
#         os.makedirs(result_cards_dir)

#     # Iterate over rows of the tmp_df
#     for index, row in tqdm(tmp_df.iterrows(), total=tmp_df.shape[0], desc="Creating Result Cards"):
#         # Get the mini result card
#         remote_result_dir = row['remote_result_dir']
#         machine = row['machine']

#         image_file_name = remote_result_dir + "_result_card.png"

#         image_file_path = os.path.join(result_cards_dir, image_file_name)

#         # if the image file doesn't exist, create it
#         if not os.path.exists(image_file_path):
#             mini_result_card = get_mini_result_card(os.path.join(results_dir, remote_result_dir), machine)
#             mini_result_card.save(image_file_path)


def find_result_card(remote_result_dir):
    """Find the result card for a given remote_result_dir."""

    image_file_name = remote_result_dir + "_result_card.png"
    image_file_path = os.path.join(result_cards_dir, image_file_name)

    print(image_file_path)

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
    tmp_df["datetime_processed"] = pd.to_datetime(tmp_df["datetime_processed"])

    create_result_cards(tmp_df)

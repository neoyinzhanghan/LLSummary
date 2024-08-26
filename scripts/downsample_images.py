import os
import pandas as pd
from PIL import Image
from tqdm import tqdm

image_folder = "/media/hdd3/riya/bma_slides/annotated_slides/predicted"
downsampled_folder = "/media/hdd3/riya/bma_slides/annotated_slides/predicted"
downsample_factor = 3

metadata = {
    "original_image_path": [],
    "downsampled_image_path": [],
    "original_image_name": [],
    "downsampled_image_name": [],
    "original_width": [],
    "original_height": [],
    "downsampled_width": [],
    "downsampled_height": [],
}

# if the downsampled folder does not exist, create it
if not os.path.exists(downsampled_folder):
    os.makedirs(downsampled_folder)

# find all jpg and png files in the image folder iteratively
all_images = []
for root, dirs, files in os.walk(image_folder):
    for file in files:
        if file.endswith(".jpg") or file.endswith(".png"):
            all_images.append(os.path.join(root, file))

# iterate over all images, downsample them and save them in the downsampled folder with the same name and folder structure
for image_path in tqdm(all_images, desc="Downsampling images"):
    image = Image.open(image_path)
    downsampled_image = image.resize(
        (image.width // downsample_factor, image.height // downsample_factor)
    )
    downsampled_image_path = image_path.replace(image_folder, downsampled_folder)

    # make sure the folder structure exists
    os.makedirs(os.path.dirname(downsampled_image_path), exist_ok=True)

    # make sure the image is saved as a jpg

    if not downsampled_image_path.endswith(".jpg"):
        downsampled_image_path = downsampled_image_path.replace(".png", ".jpg")

    downsampled_image.save(downsampled_image_path)

    metadata["original_image_path"].append(image_path)
    metadata["downsampled_image_path"].append(downsampled_image_path)
    metadata["original_width"].append(image.width)
    metadata["original_height"].append(image.height)
    metadata["downsampled_width"].append(downsampled_image.width)
    metadata["downsampled_height"].append(downsampled_image.height)
    metadata["original_image_name"].append(os.path.basename(image_path))
    metadata["downsampled_image_name"].append(os.path.basename(downsampled_image_path))

# save metadata to a csv file
df = pd.DataFrame(metadata)
df.to_csv(os.path.join(downsampled_folder, "downsampling_metadata.csv"), index=False)

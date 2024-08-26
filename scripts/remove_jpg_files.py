import os

image_dir = "/media/hdd3/riya/bma_slides/annotated_slides/predicted"

# remove all jpg files in the image directory
for root, dirs, files in os.walk(image_dir):
    for file in files:
        if file.endswith(".jpg"):
            os.remove(os.path.join(root, file))

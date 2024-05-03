import os
from PIL import Image

def get_screenshot_size(screenshot_folder_path):
    # Note: this assumes all screenshots are of the same size and only gets the first one
    # ALL CREDITS TO THE SILICA DEV FOR THE LOGIC HERE
    for file in os.listdir(screenshot_folder_path):
        if file.lower() == ".ds_store": 
            continue

        with Image.open(f"{screenshot_folder_path}/{file}") as img:
            width, height = img.size
            #  Make sure it's not too big.
            #  If height > width, make height 300, width proportional.
            #  If height < width, make width 160, height proportional.
            if height > width:
                width = round((400 * width)/height)
                height = 400
            else:
                height = round((200 * height) / width)
                width = 200
            return "{" + str(width) + "," + str(height) + "}"

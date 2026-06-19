import os
import shutil
import time
from pathlib import Path

# ======= SETUP PATHS & RULES =======
source_folder = Path.home() / "Downloads"
zip_folder = Path.home() / "Downloads" / "ZipFiles"

# ======= Rules for sorting =======
sorting_rules = {
    ".pdf": Path.home() / "Documents" / "PDFs",
    ".docx": Path.home() / "Documents" / "WordDocs",
    ".jpg": Path.home() / "Pictures",
    ".png": Path.home() / "Pictures",
    ".zip": zip_folder,
    ".jpeg": Path.home() / "Pictures" / "JPEGs",
}

# STEP 1: SORT THE FILES

print(f"Scanning your Inventory: {source_folder}")

for item in source_folder.iterdir():
    if item.is_file():
        file_extension = item.suffix.lower() # If .Pdf -> .pdf

        if file_extension in sorting_rules:
            destination_folder = sorting_rules[file_extension]

            if not destination_folder.exists():
                destination_folder.mkdir(parents=True, exist_ok=True)

            destination_file_path = destination_folder / item.name
            shutil.move(str(item), str(destination_file_path))
            print(f"Moved: {item.name} -> to -> {destination_folder.name}")

print("Sorting complete!\n")

# CLEAN UP OLD FILES

print(f"Checking for old files to clean up in: {zip_folder}")

# How old should a file be to delete it? (In days, you can change it here)
days_threshold = 14

# Convert days into seconds because Python measures file age in seconds
# (60 seconds * 60 minutes * 24 hours = 1 day)
seconds_in_a_day = 60 * 60 * 24
max_age_seconds = days_threshold * seconds_in_a_day

# Get the current time right now
current_time = time.time()

# Check if the folder even exists before looking inside
if zip_folder.exists():
    for file_item in zip_folder.iterdir():
        if file_item.is_file():

            # Find out when the file was last modified/saved
            file_modified_time = file_item.stat().st_mtime

            # Calculate how many seconds old the file is
            file_age_seconds = current_time - file_modified_time

            # If the file is older than our limit, delete it!
            if file_age_seconds > max_age_seconds:
                file_item.unlink()  # .unlink() is the Python way to delete a file
                print(f"Deleted old file: {file_item.name}")

print("Butler task complete!")
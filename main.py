import os
import shutil # Utility functions for copying and archiving files and directory trees.
import time # This helps to do time operations
import zipfile  # This helps us bundle files into a single zip
from pathlib import Path #This module provides classes to represent abstract paths and concrete paths.

# ======= SETUP PATHS & RULES =======
source_folder = Path.home() / "Downloads"
zip_folder = Path.home() / "Downloads" / "ZipFiles"
pictures_folder = Path.home() / "Pictures"
archive_folder = Path.home() / "Documents" / "Archives"

# ======= Rules for sorting =======
sorting_rules = {
    ".pdf": Path.home() / "Documents" / "PDFs",
    ".docx": Path.home() / "Documents" / "WordDocs",
    ".jpg": pictures_folder,
    ".png": pictures_folder,
    ".zip": zip_folder,
    ".jpeg": Path.home() / "Pictures" / "JPEGs",
}

# STEP 1: SORT THE FILES

print(f"Scanning your Inventory: {source_folder}")

for item in source_folder.iterdir():
    if item.is_file():
        file_extension = item.suffix.lower()  # If .Pdf -> .pdf

        if file_extension in sorting_rules:
            destination_folder = sorting_rules[file_extension]

            if not destination_folder.exists():
                destination_folder.mkdir(parents=True, exist_ok=True)

            destination_file_path = destination_folder / item.name
            shutil.move(str(item), str(destination_file_path))
            print(f"Moved: {item.name} -> to -> {destination_folder.name}")

print("Sorting complete!\n")

# STEP 2: CLEAN UP OLD FILES

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

print("Cleanup complete!\n")

# STEP 3: ARCHIVE OLD MEDIA

print(f"Checking for media files to archive in: {pictures_folder}")

# For testing, change it to 0 means "archive everything immediately". Change to 30 later!
archive_threshold_days = 30
max_media_age_seconds = archive_threshold_days * seconds_in_a_day

# Create the Archives folder if it's missing
if not archive_folder.exists():
    archive_folder.mkdir(parents=True, exist_ok=True)

# This is where our compressed zip will live
zip_archive_path = archive_folder / "media_archive.zip"

if pictures_folder.exists():
    # 'a' mode lets us continuously ADD files to the zip instead of overwriting it
    with zipfile.ZipFile(zip_archive_path, 'a') as my_zip:

        for media_item in pictures_folder.iterdir():
            if media_item.is_file():

                # Check how old the photo/video is
                media_modified_time = media_item.stat().st_mtime
                media_age_seconds = current_time - media_modified_time

                if media_age_seconds >= max_media_age_seconds :
                    # 1. Put a copy of the file inside the zip archive
                    my_zip.write(media_item, arcname=media_item.name,)
                    print(f"Archived: {media_item.name} -> added to zip archive")

                    # 2. Safely delete the original file outside the zip
                    media_item.unlink()

print("Archiving complete!\n")
print("Butler task complete!")
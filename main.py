import os
import shutil  # Utility functions for copying and archiving files and directory trees.
import time  # This helps to do time operations
import zipfile  # This helps us bundle files into a single zip
from pathlib import Path  # This module provides classes to represent abstract paths and concrete paths.
import requests  # To send data over the internet to Discord

# ======= SETUP PATHS & RULES =======
source_folder = Path.home() / "Downloads"
zip_folder = Path.home() / "Downloads" / "ZipFiles"
pictures_folder = Path.home() / "Pictures"
archive_folder = Path.home() / "Documents" / "Archives"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1517472374822273168/QJ5VfhqudMOMq5MF5COT8F4WxkmyyVFTU652KkPZurz9w3bqvs_rCWCp3riR6O2oivh-"

# ======= Rules for sorting =======
sorting_rules = {
    ".pdf": Path.home() / "Documents" / "PDFs",
    ".docx": Path.home() / "Documents" / "WordDocs",
    ".jpg": pictures_folder,
    ".png": pictures_folder,
    ".zip": zip_folder,
    ".jpeg": Path.home() / "Pictures" / "JPEGs",
    ".mp4": Path.home() / "Videos",
    ".mp3": Path.home() / "Music",
    ".txt": Path.home() / "Documents" / "TextFiles",
    ".csv": Path.home() / "Documents" / "CSVFiles",
    ".exe": Path.home() / "Documents" / "Executables"
}

# ======= Changeable thresholds =======
# Adjust these values to control cleanup and archiving behavior.
days_threshold = 14
archive_threshold_days = 30

# NEW: Blank lists to store our butler's activity logs
moved_log = []
deleted_log = []
archived_log = []

# Helper functions for Discord notifications

def send_discord_notification(message_text):
    if not DISCORD_WEBHOOK_URL or "PASTE_YOUR_COPIED_DISCORD_URL_HERE" in DISCORD_WEBHOOK_URL:
        print("Discord webhook URL not set. Skipping Discord notification.")
        return False

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json={"content": message_text})

        if response.status_code == 204:
            print("Discord notification sent successfully.")
            return True

        print(f"Discord replied with an error code: {response.status_code}")
        return False

    except Exception as e:
        print(f"Could not connect to Discord. Error: {e}")
        return False


def build_discord_start_message():
    return (
        "🎩 **Digital Butler is starting** 🔔\n\n"
        f"**Sorting:** Files from `{source_folder}` using the configured rules.\n"
        f"**Cleanup:** Remove `.zip` files older than {days_threshold} days from `{zip_folder}`.\n"
        f"**Archiving:** Compress pictures/media older than {archive_threshold_days} days from `{pictures_folder}`.\n\n"
        "I will send a completion summary once the job is finished."
    )


def build_discord_report():
    report = "🎩 **Digital Butler Activity Report** 🔔\n\n"

    if moved_log:
        report += "**📁 Files Sorted:**\n" + "\n".join(moved_log) + "\n\n"
    else:
        report += "**📁 Files Sorted:** _None_\n\n"

    if deleted_log:
        report += "**🗑️ Files Cleaned Up:**\n" + "\n".join(deleted_log) + "\n\n"
    else:
        report += "**🗑️ Files Cleaned Up:** _None_\n\n"

    if archived_log:
        report += "**📦 Files Archived:**\n" + "\n".join(archived_log) + "\n\n"
    else:
        report += "**📦 Files Archived:** _None_\n\n"

    report += "---\n_This message was generated automatically by Digital Butler._"
    return report

# STEP 1: SORT THE FILES

print(f"Scanning your Inventory: {source_folder}")

send_discord_notification(build_discord_start_message())

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

            # Record what was moved and where
            moved_log.append(f"🔹 `{item.name}` ➡️ **{destination_folder.name}**")

print("Sorting complete!\n")

# STEP 2: CLEAN UP OLD FILES

print(f"Checking for old files to clean up in: {zip_folder}")

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

                # Record what was deleted
                deleted_log.append(f"❌ `{file_item.name}`")

print("Cleanup complete!\n")

# STEP 3: ARCHIVE OLD MEDIA

print(f"Checking for media files to archive in: {pictures_folder}")

# For testing, change it to 0 which means "archive everything immediately". Change to 30 later!
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

                if media_age_seconds >= max_media_age_seconds:
                    # 1. Put a copy of the file inside the zip archive
                    my_zip.write(media_item, arcname=media_item.name)
                    print(f"Archived: {media_item.name} -> added to zip archive")

                    # Record what was archived
                    archived_log.append(f"📦 `{media_item.name}`")

                    # 2. Safely delete the original file outside the zip
                    media_item.unlink()

print("Archiving complete!\n")

# STEP 4: DISCORD NOTIFICATION

print("Compiling summary report for Discord...")

send_discord_notification(build_discord_report())

print("Butler task complete!")
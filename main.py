import os
import shutil  # Utility functions for copying and archiving files and directory trees.
import time  # This helps to do time operations
import zipfile  # This helps us bundle files into a single zip
import logging  # For logging activities to file with timestamps
from pathlib import Path  # This module provides classes to represent abstract paths and concrete paths.
import requests  # To send data over the internet to Discord

# ======= SETUP LOGGING =======
log_folder = Path.home() / "Documents" / "Butler_Logs"
log_folder.mkdir(parents=True, exist_ok=True)
log_file = log_folder / f"butler_{time.strftime('%Y-%m-%d_%H-%M-%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()  # Also print to console
    ]
)
logger = logging.getLogger(__name__)
logger.info("🎩 Digital Butler started")

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
archive_min_file_size_mb = 5  # Only archive files larger than 5 MB (set to 0 to disable size check)
compression_level = zipfile.ZIP_DEFLATED  # Compression: ZIP_STORED (0, fastest) or ZIP_DEFLATED (6, best compression)

# NEW: Blank lists to store our butler's activity logs
moved_log = []
deleted_log = []
archived_log = []

# Track file sizes for statistics
moved_sizes = []  # Track sizes of moved files
deleted_sizes = []  # Track sizes of deleted files
archived_sizes = []  # Track sizes of archived files

# Helper functions for Discord notifications

def send_discord_notification(message_text, retries=3):
    if not DISCORD_WEBHOOK_URL or "PASTE_YOUR_COPIED_DISCORD_URL_HERE" in DISCORD_WEBHOOK_URL:
        logger.warning("Discord webhook URL not set. Skipping Discord notification.")
        print("Discord webhook URL not set. Skipping Discord notification.")
        return False

    for attempt in range(retries):
        try:
            response = requests.post(DISCORD_WEBHOOK_URL, json={"content": message_text}, timeout=10)

            if response.status_code == 204:
                logger.info("Discord notification sent successfully.")
                print("Discord notification sent successfully.")
                return True

            logger.error(f"Discord replied with error code: {response.status_code}")
            print(f"Discord replied with an error code: {response.status_code}")
            
            if attempt < retries - 1:
                logger.info(f"Retrying Discord notification (attempt {attempt + 2}/{retries})...")
                time.sleep(2)  # Wait 2 seconds before retrying

        except requests.exceptions.Timeout:
            logger.warning(f"Discord request timeout (attempt {attempt + 1}/{retries})")
            print(f"Discord request timed out. Attempt {attempt + 1}/{retries}")
            if attempt < retries - 1:
                time.sleep(2)

        except Exception as e:
            logger.error(f"Could not connect to Discord. Error: {e} (attempt {attempt + 1}/{retries})")
            print(f"Could not connect to Discord. Error: {e}")
            if attempt < retries - 1:
                time.sleep(2)

    logger.error("Failed to send Discord notification after all retry attempts")
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

    # Helper function to format bytes to human-readable sizes
    def format_size(bytes_size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f} TB"

    # Sorting statistics
    if moved_log:
        total_moved = sum(moved_sizes)
        report += f"**📁 Files Sorted:** {len(moved_log)} files, {format_size(total_moved)} total\n"
        report += "\n".join(moved_log) + "\n\n"
    else:
        report += "**📁 Files Sorted:** _None_\n\n"

    # Cleanup statistics
    if deleted_log:
        total_deleted = sum(deleted_sizes)
        report += f"**🗑️ Files Cleaned Up:** {len(deleted_log)} files, {format_size(total_deleted)} total\n"
        report += "\n".join(deleted_log) + "\n\n"
    else:
        report += "**🗑️ Files Cleaned Up:** _None_\n\n"

    # Archive statistics
    if archived_log:
        total_archived = sum(archived_sizes)
        report += f"**📦 Files Archived:** {len(archived_log)} files, {format_size(total_archived)} total\n"
        report += "\n".join(archived_log) + "\n\n"
    else:
        report += "**📦 Files Archived:** _None_\n\n"

    report += "---\n_This message was generated automatically by Digital Butler._"
    return report

# STEP 1: SORT THE FILES

logger.info(f"Scanning your Inventory: {source_folder}")
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
            try:
                file_size = item.stat().st_size  # Get file size in bytes
                shutil.move(str(item), str(destination_file_path))
                logger.info(f"Moved: {item.name} ({file_size / 1024:.1f} KB) -> {destination_folder.name}")
                print(f"Moved: {item.name} -> to -> {destination_folder.name}")

                # Record what was moved and where
                moved_log.append(f"🔹 `{item.name}` ➡️ **{destination_folder.name}**")
                moved_sizes.append(file_size)
            except (OSError, PermissionError) as e:
                logger.error(f"Failed to move {item.name}: {e}")
                print(f"❌ Error moving {item.name}: {e}")

print("Sorting complete!\n")
logger.info("Sorting complete")

# STEP 2: CLEAN UP OLD FILES

logger.info(f"Checking for old files to clean up in: {zip_folder}")
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
                try:
                    file_size = file_item.stat().st_size  # Get file size before deletion
                    file_item.unlink()  # .unlink() is the Python way to delete a file
                    logger.info(f"Deleted old file: {file_item.name} ({file_size / 1024:.1f} KB)")
                    print(f"Deleted old file: {file_item.name}")

                    # Record what was deleted
                    deleted_log.append(f"❌ `{file_item.name}`")
                    deleted_sizes.append(file_size)
                except (OSError, PermissionError) as e:
                    logger.warning(f"Could not delete {file_item.name}: {e}")
                    print(f"⚠️ Could not delete {file_item.name}: {e}")

print("Cleanup complete!\n")
logger.info("Cleanup complete")

# STEP 3: ARCHIVE OLD MEDIA

print(f"Checking for media files to archive in: {pictures_folder}")
logger.info(f"Checking for media files to archive in: {pictures_folder}")

# For testing, change it to 0 which means "archive everything immediately". Change to 30 later!
max_media_age_seconds = archive_threshold_days * seconds_in_a_day

# Create the Archives folder if it's missing
if not archive_folder.exists():
    archive_folder.mkdir(parents=True, exist_ok=True)

# This is where our compressed zip will live
zip_archive_path = archive_folder / "media_archive.zip"

if pictures_folder.exists():
    # 'a' mode lets us continuously ADD files to the zip instead of overwriting it
    try:
        with zipfile.ZipFile(zip_archive_path, 'a', compression=compression_level) as my_zip:

            for media_item in pictures_folder.iterdir():
                if media_item.is_file():

                    # Check how old the photo/video is
                    media_modified_time = media_item.stat().st_mtime
                    media_age_seconds = current_time - media_modified_time
                    file_size = media_item.stat().st_size  # Get file size
                    file_size_mb = file_size / 1024 / 1024

                    # Check both age and size thresholds
                    age_meets_criteria = media_age_seconds >= max_media_age_seconds
                    size_meets_criteria = (archive_min_file_size_mb == 0) or (file_size_mb >= archive_min_file_size_mb)

                    if age_meets_criteria and size_meets_criteria:
                        try:
                            # 1. Put a copy of the file inside the zip archive
                            my_zip.write(media_item, arcname=media_item.name)
                            logger.info(f"Archived: {media_item.name} ({file_size_mb:.1f} MB) - Age: {media_age_seconds/86400:.0f} days")
                            print(f"Archived: {media_item.name} -> added to zip archive")

                            # Record what was archived
                            archived_log.append(f"📦 `{media_item.name}`")
                            archived_sizes.append(file_size)

                            # 2. Safely delete the original file outside the zip
                            media_item.unlink()
                        except (OSError, PermissionError) as e:
                            logger.warning(f"Could not archive {media_item.name}: {e}")
                            print(f"⚠️ Could not archive {media_item.name}: {e}")
    except zipfile.BadZipFile as e:
        logger.error(f"Zip archive is corrupted or unreadable: {e}")
        print(f"❌ Archive issue: {e}")

print("Archiving complete!\n")
logger.info("Archiving complete")

# STEP 4: DISCORD NOTIFICATION

print("Compiling summary report for Discord...")

send_discord_notification(build_discord_report())

print("Butler task complete!")
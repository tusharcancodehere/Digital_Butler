<h1 align="center">🤵‍♂️ Digital Butler</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Maintained%3F-yes-brightgreen.svg" alt="Maintained">
</p>

<p align="center">
  <strong>An automated background service that actively manages your digital workspace based on customizable rules.</strong>
</p>

---

## 📖 About The Project

Instead of relying on a simple, manual file sorter, **Digital Butler** runs silently in the background, watching your designated local directories (like `Downloads` and `Desktop`). It organizes files by extension, cleans up temporary clutter, archives old data, and seamlessly backs up critical documents to the cloud.

### ✨ Key Features

* **Smart Sorting:** Automatically categorizes files by their extensions into designated folders.
* **Automated Cleanup:** Deletes temporary or installer files (e.g., `.dmg`, `.tmp`, `.exe`) older than a set number of days.
* **Smart Archiving:** Zips unused files that are older than 30 days to free up disk space.
* **Cloud Backup Integration:** Uploads critical documents (like PDFs and DOCX files) directly to an AWS S3 bucket or Google Drive.
* **Rule-Based Configuration:** Driven entirely by a `.yaml` or `.json` file, allowing complete customization of sorting rules and timelines.
* **Notification System:** Sends automated summary reports to a Discord channel (via Webhooks) or via Email, detailing exactly what was moved, deleted, or backed up.

## 🛠 Built With

* **File System Manipulation:** `os`, `shutil`, `pathlib`
* **Task Scheduling:** `schedule` / `cron`
* **Cloud APIs:** `boto3` (AWS) / `google-api-python-client` (Google Drive)
* **Notifications:** `requests` (Discord Webhooks), `smtplib` (Email)

---

## 🚀 Getting Started

Follow these steps to get your Digital Butler up and running on your local machine.

### Prerequisites

* Python 3.8 or higher
* A Discord Webhook URL (optional, for notifications)
* AWS Credentials or Google Drive API Service Account (optional, for cloud backups)

### Installation

1. **Clone the repository:**
```bash
   git clone [https://github.com/yourusername/digital-butler.git](https://github.com/yourusername/digital-butler.git)
   cd digital-butler
   python main.py

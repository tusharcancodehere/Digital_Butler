# 🤵‍♂️ Digital Butler

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Maintained%3F-yes-brightgreen.svg" alt="Maintained">
</p>

<p align="center">
  <strong>An automated local script that cleans, sorts, archives, and manages your digital workspace with smart reporting.</strong>
</p>

---

## 📖 About The Project

**Digital Butler** is a Python automation script built to take over your boring computer chores. Instead of manually organizing messy folders, this script scans your target directories, groups your files cleanly, purges old temporary clutter, archives old photos/videos, and sends a beautifully formatted summary report straight to your private Discord server.

### ✨ Key Features

* **Step 1: Smart Sorting:** Instantly categorizes files from your `Downloads` directory (like `.pdf`, `.docx`, `.jpg`, `.png`, `.zip`, `.jpeg`) into distinct folders automatically.
* **Step 2: Automated Cleanup:** Identifies old compressed files sitting inside your `ZipFiles` folder and permanently deletes items older than 14 days to recover hard drive space.
* **Step 3: Media Archiving:** Scans your loose `Pictures` folder, packs images older than 30 days into a single compressed `media_archive.zip` file, and clears out the originals.
* **Step 4: Live Discord Summary Reports:** Gathers a detailed list of every single action performed by the butler (names of files moved, deleted, and archived) and posts an interactive summary directly to your Discord via Webhooks.

---

## 🛠 Built With

* **Core Language:** Python 3
* **File System Operations:** `pathlib`, `shutil`
* **Compression Engine:** `zipfile`
* **Time Management:** `time`
* **Network & Webhooks:** `requests`

---

## 🚀 Getting Started

Follow these simple steps to run your own personal Digital Butler locally.

### Prerequisites

Make sure you have Python installed on your machine. You will also need a Discord server where you can create a Webhook URL.

### Installation & Setup

#### 1. Clone the repository

```bash
git clone https://github.com/tusharcancodehere/Digital_Butler.git
cd Digital_Butler
```

#### 2. Install the required package

Open your terminal and run:

```bash
pip install requests
```

#### 3. Configure your Discord Webhook

* Open your Discord Server Settings.
* Navigate to **Integrations → Webhooks**.
* Create a new webhook.
* Copy the webhook URL.
* Paste it into the `DISCORD_WEBHOOK_URL` variable in `main.py`:

```python
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/your-secret-link-here"
```

---

## 🏃‍♂️ Running the Butler

To run your workspace automation chores, execute the script from your terminal or click the **Run** button inside PyCharm:

```bash
python main.py
```

# Modern YouTube Video Downloader

This is a YouTube Video Downloader built using Flet and yt-dlp. The application allows users to download YouTube videos with embedded chapters.

## Features

- Download YouTube videos in 720p, 480p, and 360p quality.
- Select custom download paths.
- View download progress.

## Requirements

- Python 3.7 or higher
- `yt-dlp`
- `flet`

## Setup Instructions

### Step 1: Clone the Repository

```sh
git clone https://github.com/your-repository/modern-youtube-downloader.git
cd modern-youtube-downloader
```

### Step 2: Create a Virtual Environment
It is recommended to use a virtual environment to manage dependencies.
```sh
python -m venv venv
.venv\Scripts\activate
```

### Step 2: Install Dependencies

```sh
pip install -r requirements.txt
```

### Step 3: Run the Application

```sh
flet run
```

## Usage Instructions
- **Enter YouTube URL:** Copy and paste the YouTube video URL into the "YouTube Video URL" field.
- **Select Quality:** Choose the desired video quality from the dropdown menu.
- **Past Download Path:** By default, the download path is set to your Downloads folder.
To select a different path, Past the desired folder path to the text field.
- **Download Video:** Click the "Download" button to start downloading the video.
- **Progress:** The progress bar and text will update to show the download status.
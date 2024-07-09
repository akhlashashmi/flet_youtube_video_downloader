import flet as ft
import subprocess
import threading
import json
import os

# Global variable to keep track of the process
download_process = None


def main(page: ft.Page):
    page.title = "Modern YouTube Video Downloader"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 20

    # Header
    header = ft.Text(
        "YouTube Downloader",
        theme_style="headlineMedium",
        weight=ft.FontWeight.BOLD,
        color=ft.colors.AMBER_ACCENT,
    )

    # URL input field
    url_input = ft.TextField(
        label="YouTube Video URL",
        width=400,
        border_color=ft.colors.AMBER_ACCENT,
        label_style=ft.TextStyle(color=ft.colors.AMBER_ACCENT),
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        border_radius=15,
        border_width=0.5,
    )

    # Quality selection dropdown
    quality_dropdown = ft.Dropdown(
        label="Select Quality",
        width=400,
        border_color=ft.colors.AMBER_ACCENT,
        label_style=ft.TextStyle(color=ft.colors.AMBER_ACCENT),
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        options=[
            ft.dropdown.Option("720p"),
            ft.dropdown.Option("480p"),
            ft.dropdown.Option("360p"),
        ],
        border_radius=15,
        border_width=0.5,
    )

    # Video title and thumbnail
    video_title = ft.Text(
        "",
        theme_style="headlineSmall",
        weight=ft.FontWeight.BOLD,
        color=ft.colors.WHITE,
    )
    video_thumbnail = ft.Image(src="", width=200, height=200, fit=ft.ImageFit.CONTAIN)

    # Progress bar and text
    progress_text = ft.Text(
        "Progress: 0%", theme_style="bodyMedium", color=ft.colors.WHITE
    )
    progress_bar = ft.ProgressBar(
        width=400, color=ft.colors.AMBER_ACCENT, bgcolor=ft.colors.AMBER_ACCENT_100
    )

    # Download path input field
    download_path_input = ft.TextField(
        label="Download Path",
        value=os.path.expanduser("~\\Downloads"),  # Default path
        width=400,
        border_color=ft.colors.AMBER_ACCENT,
        label_style=ft.TextStyle(color=ft.colors.AMBER_ACCENT),
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        border_radius=15,
        border_width=0.5,
    )

    # Function to fetch video info
    def fetch_video_info(url):
        ytdlp_command = ["yt-dlp", "-j", url]
        process = subprocess.Popen(
            ytdlp_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print(f"Error: {stderr}")
            return None

        return json.loads(stdout)

    # Function to download the video
    def download_video(e):
        global download_process

        url = url_input.value
        quality = quality_dropdown.value
        download_path = download_path_input.value

        if not url:
            progress_text.value = "Please enter a URL."
            page.update()
            return
        if not quality:
            progress_text.value = "Please select a quality."
            page.update()
            return
        if not os.path.isdir(download_path):
            progress_text.value = "Please enter a valid download path."
            page.update()
            return

        info = fetch_video_info(url)
        if info:
            video_title.value = info.get("title", "No title found")
            video_thumbnail.src = info.get("thumbnail", "")
            page.update()
        else:
            progress_text.value = "Failed to fetch video info."
            page.update()
            return

        quality_map = {
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
        }

        output_template = os.path.join(download_path, "%(title)s.%(ext)s")
        ytdlp_command = [
            "yt-dlp",
            "-f",
            quality_map[quality],
            "--merge-output-format",
            "mkv",
            "--embed-chapters",
            "--output",
            output_template,
            url,
        ]

        def run_command():
            global download_process
            download_process = subprocess.Popen(
                ytdlp_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )
            for line in download_process.stdout:
                if "Downloading" in line:
                    progress_text.value = line.strip()
                    page.update()
                elif "%" in line:
                    parts = line.split()
                    for part in parts:
                        if "%" in part:
                            try:
                                percent = float(part.strip("%"))
                                progress_bar.value = percent / 100
                                progress_text.value = f"Progress: {percent}%"
                                page.update()
                            except ValueError:
                                continue

            progress_text.value = "Download completed!"
            page.update()
            download_process = None

        threading.Thread(target=run_command).start()

    # Download button
    download_button = ft.ElevatedButton(
        text= "Download" if download_process == None else "Downloading...",
        on_click=download_video,
        bgcolor=ft.colors.AMBER_ACCENT,
        color=ft.colors.BLACK,
        icon=ft.icons.DOWNLOAD_ROUNDED,
        icon_color=ft.colors.BLACK,
    )

    # Layout the controls in a column inside a container
    container = ft.Container(
        content=ft.Column(
            [
                header,
                url_input,
                quality_dropdown,
                download_path_input,
                video_title,
                video_thumbnail if video_thumbnail.src != "" else ft.Container(),
                ft.Row(
                    [
                        download_button,
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                progress_text,
                progress_bar,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        ),
        width=500,
        padding=20,
        border_radius=10,
    )

    page.add(container)


ft.app(target=main)
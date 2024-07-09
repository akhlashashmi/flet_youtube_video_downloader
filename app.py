import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import threading
import os
import json
from PIL import Image, ImageTk
import requests
import signal

# Global variable to keep track of the process
download_process = None

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("600x400")
        
        # Video URL
        self.url_label = ttk.Label(root, text="YouTube Video URL")
        self.url_label.pack(pady=5)
        self.url_entry = ttk.Entry(root, width=50)
        self.url_entry.pack(pady=5)
        
        # Quality selection
        self.quality_label = ttk.Label(root, text="Select Quality")
        self.quality_label.pack(pady=5)
        self.quality_var = tk.StringVar()
        self.quality_dropdown = ttk.Combobox(root, textvariable=self.quality_var, values=["720p", "480p", "360p"])
        self.quality_dropdown.pack(pady=5)
        
        # Video info
        self.video_title_label = ttk.Label(root, text="", font=("Helvetica", 10, "bold"))
        self.video_title_label.pack(pady=5)
        self.video_thumbnail_label = ttk.Label(root)
        self.video_thumbnail_label.pack(pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=5)
        self.progress_label = ttk.Label(root, text="Progress: 0%")
        self.progress_label.pack(pady=5)
        
        # Buttons
        self.download_button = ttk.Button(root, text="Download", command=self.start_download)
        self.download_button.pack(pady=5)
        self.pause_button = ttk.Button(root, text="Pause", command=self.pause_download)
        self.pause_button.pack(pady=5)
        self.resume_button = ttk.Button(root, text="Resume", command=self.resume_download)
        self.resume_button.pack(pady=5)
        self.stop_button = ttk.Button(root, text="Stop", command=self.stop_download)
        self.stop_button.pack(pady=5)
    
    def fetch_video_info(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a URL.")
            return None

        ytdlp_command = ["yt-dlp", "-j", url]
        process = subprocess.Popen(ytdlp_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            messagebox.showerror("Error", stderr)
            return None

        info = json.loads(stdout)
        title = info.get("title", "No title found")
        thumbnail_url = info.get("thumbnail", "")
        return title, thumbnail_url

    def update_thumbnail(self, thumbnail_url):
        try:
            image_data = Image.open(requests.get(thumbnail_url, stream=True).raw)
            image_data = image_data.resize((200, 200), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(image_data)
            self.video_thumbnail_label.config(image=img)
            self.video_thumbnail_label.image = img
        except Exception as e:
            print(f"Error loading thumbnail: {e}")
    
    def start_download(self):
        global download_process

        url = self.url_entry.get()
        quality = self.quality_var.get()
        if not url:
            messagebox.showerror("Error", "Please enter a URL.")
            return
        if not quality:
            messagebox.showerror("Error", "Please select a quality.")
            return

        video_info = self.fetch_video_info()
        if not video_info:
            return
        
        title, thumbnail_url = video_info
        self.video_title_label.config(text=title)
        self.update_thumbnail(thumbnail_url)

        quality_map = {
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
        }

        ytdlp_command = [
            "yt-dlp",
            "-f", quality_map[quality],
            "--merge-output-format", "mkv",
            "--embed-chapters",
            "--output", "%(title)s.%(ext)s",
            url
        ]

        def run_command():
            global download_process
            self.progress["value"] = 0
            download_process = subprocess.Popen(ytdlp_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            for line in download_process.stdout:
                if "Downloading" in line:
                    self.progress_label.config(text=line.strip())
                    self.root.update_idletasks()
                elif "%" in line:
                    parts = line.split()
                    for part in parts:
                        if "%" in part:
                            try:
                                percent = float(part.strip('%'))
                                self.progress["value"] = percent
                                self.progress_label.config(text=f"Progress: {percent}%")
                                self.root.update_idletasks()
                            except ValueError:
                                continue

            self.progress_label.config(text="Download completed!")
            download_process = None

        threading.Thread(target=run_command).start()

    def pause_download(self):
        global download_process
        if download_process:
            download_process.send_signal(signal.SIGBREAK)
            self.progress_label.config(text="Download paused")
            self.root.update_idletasks()

    def resume_download(self):
        global download_process
        if download_process:
            download_process.send_signal(signal.SIGABRT)
            self.progress_label.config(text="Download resumed")
            self.root.update_idletasks()

    def stop_download(self):
        global download_process
        if download_process:
            download_process.terminate()
            self.progress_label.config(text="Download stopped")
            self.progress["value"] = 0
            self.root.update_idletasks()
            download_process = None

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()

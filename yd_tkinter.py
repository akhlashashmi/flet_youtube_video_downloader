import tkinter as tk
from tkinter import ttk
import subprocess
import threading

class YTDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")

        # URL input field
        self.url_label = tk.Label(root, text="YouTube Video URL")
        self.url_label.grid(row=0, column=0, padx=10, pady=5)
        self.url_input = tk.Entry(root, width=50)
        self.url_input.grid(row=0, column=1, padx=10, pady=5)

        # Quality selection dropdown
        self.quality_label = tk.Label(root, text="Select Quality")
        self.quality_label.grid(row=1, column=0, padx=10, pady=5)
        self.quality_var = tk.StringVar()
        self.quality_dropdown = ttk.Combobox(root, textvariable=self.quality_var, values=["720p", "480p", "360p"], state="readonly")
        self.quality_dropdown.grid(row=1, column=1, padx=10, pady=5)
        self.quality_dropdown.current(0)  # set default value

        # Download button
        self.download_button = tk.Button(root, text="Download", command=self.download_video)
        self.download_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Progress text
        self.progress_text = tk.StringVar()
        self.progress_label = tk.Label(root, textvariable=self.progress_text)
        self.progress_label.grid(row=3, column=0, columnspan=2, pady=5)
        self.progress_text.set("Progress: 0%")

        # Progress bar
        self.progress_bar = ttk.Progressbar(root, length=400, mode="determinate")
        self.progress_bar.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

    def download_video(self):
        url = self.url_input.get()
        quality = self.quality_var.get()
        if not url:
            self.progress_text.set("Please enter a URL.")
            return
        if not quality:
            self.progress_text.set("Please select a quality.")
            return

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
            process = subprocess.Popen(ytdlp_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            for line in process.stdout:
                if "Downloading" in line:
                    self.progress_text.set(line.strip())
                elif "%" in line:
                    parts = line.split()
                    for part in parts:
                        if "%" in part:
                            try:
                                percent = float(part.strip('%'))
                                self.progress_bar["value"] = percent
                                self.progress_text.set(f"Progress: {percent}%")
                            except ValueError:
                                continue

            self.progress_text.set("Download completed!")

        threading.Thread(target=run_command).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = YTDownloaderApp(root)
    root.mainloop()

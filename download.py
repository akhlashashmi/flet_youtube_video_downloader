import os
import sys
from pytube import YouTube

def download_video(youtube_url):
    yt = YouTube(youtube_url)

    # Get the 720p video stream
    video_stream = yt.streams.filter(progressive=False, file_extension='mp4', res="720p").first()
    audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()

    # Download video and audio streams
    video_file = video_stream.download(filename='video.mp4')
    audio_file = audio_stream.download(filename='audio.mp4')

    # Get English subtitles
    if 'en' in yt.captions:
        caption = yt.captions['en']
        subtitle_file = 'subtitles.srt'
        with open(subtitle_file, 'w') as f:
            f.write(caption.generate_srt_captions())
    else:
        subtitle_file = None

    # Merge video, audio, and subtitles using ffmpeg
    output_file = f"{yt.title}.mkv"
    ffmpeg_command = [
        'ffmpeg', '-i', 'video.mp4', '-i', 'audio.mp4', '-c:v', 'copy', '-c:a', 'copy', '-c:s', 'mov_text'
    ]

    if subtitle_file:
        ffmpeg_command.extend(['-i', subtitle_file, '-c:s', 'mov_text'])
    
    ffmpeg_command.append(output_file)
    
    os.system(' '.join(ffmpeg_command))

    # Clean up
    os.remove('video.mp4')
    os.remove('audio.mp4')
    if subtitle_file:
        os.remove(subtitle_file)

    print(f"Downloaded and merged video saved as {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python download_youtube.py <youtube_url>")
        sys.exit(1)

    youtube_url = sys.argv[1]
    download_video(youtube_url)



# import sys
# import yt_dlp

# def download_video(url):
#     # Define options for yt-dlp
#     ydl_opts = {
#         'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
#         'subtitleslangs': ['en'],
#         'writesubtitles': True,
#         'subtitlesformat': 'srt',
#         'merge_output_format': 'mkv',
#         'outtmpl': '%(title)s.%(ext)s',
#         'postprocessors': [{
#             'key': 'FFmpegEmbedSubtitle',
#             'already_have_subtitle': False
#         }],
#         'postprocessor_args': [
#             '-c:s', 'mov_text'
#         ]
#     }

#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         ydl.download([url])

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print("Usage: python download_youtube.py <youtube_url>")
#         sys.exit(1)

#     youtube_url = sys.argv[1]
#     download_video(youtube_url)

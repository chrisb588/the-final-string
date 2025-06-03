#!/usr/bin/env python3
"""
YouTube to MP3 Converter
Converts YouTube videos to MP3 audio files using yt-dlp

Requirements:
    pip install yt-dlp

Optional (for better audio processing):
    - FFmpeg installed on your system
"""

import os
import sys
import re
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("Error: yt-dlp is not installed.")
    print("Install it with: pip install yt-dlp")
    sys.exit(1)


class YouTubeToMP3Converter:
    def __init__(self, output_dir="downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # yt-dlp options for MP3 conversion
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'audioquality': '192',  # 192 kbps
            'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'postprocessor_args': [
                '-ar', '44100',  # Sample rate
            ],
            'prefer_ffmpeg': True,
        }
    
    def is_valid_youtube_url(self, url):
        """Validate YouTube URL"""
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        return youtube_regex.match(url) is not None
    
    def get_video_info(self, url):
        """Get video information without downloading"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0)
                }
        except Exception as e:
            print(f"Error getting video info: {str(e)}")
            return None
    
    def convert_seconds_to_time(self, seconds):
        """Convert seconds to MM:SS format"""
        if not seconds:
            return "Unknown"
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def download_and_convert(self, url):
        """Download YouTube video and convert to MP3"""
        if not self.is_valid_youtube_url(url):
            print("Error: Invalid YouTube URL")
            return False
        
        # Get video info first
        print("Getting video information...")
        info = self.get_video_info(url)
        
        if info:
            print(f"Title: {info['title']}")
            print(f"Duration: {self.convert_seconds_to_time(info['duration'])}")
            print(f"Uploader: {info['uploader']}")
            print()
        
        try:
            print("Downloading and converting to MP3...")
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([url])
            
            print(f"✅ Successfully converted to MP3!")
            print(f"📁 Saved to: {self.output_dir.absolute()}")
            return True
            
        except yt_dlp.DownloadError as e:
            print(f"❌ Download failed: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            return False
    
    def batch_convert(self, urls):
        """Convert multiple YouTube URLs to MP3"""
        successful = 0
        failed = 0
        
        for i, url in enumerate(urls, 1):
            print(f"\n--- Converting {i}/{len(urls)} ---")
            print(f"URL: {url}")
            
            if self.download_and_convert(url):
                successful += 1
            else:
                failed += 1
        
        print(f"\n--- Batch Conversion Complete ---")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")


def main():
    converter = YouTubeToMP3Converter()
    
    print("🎵 YouTube to MP3 Converter")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Convert single video")
        print("2. Convert multiple videos")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            url = input("\nEnter YouTube URL: ").strip()
            if url:
                converter.download_and_convert(url)
            else:
                print("No URL provided.")
        
        elif choice == '2':
            print("\nEnter YouTube URLs (one per line, press Enter twice when done):")
            urls = []
            while True:
                url = input().strip()
                if not url:
                    break
                urls.append(url)
            
            if urls:
                converter.batch_convert(urls)
            else:
                print("No URLs provided.")
        
        elif choice == '3':
            print("Goodbye! 👋")
            break
        
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    # Check if FFmpeg is available
    try:
        import subprocess
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL, 
                      check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Warning: FFmpeg not found. Audio quality may be limited.")
        print("   Install FFmpeg for better audio processing.")
        print()
    
    main()
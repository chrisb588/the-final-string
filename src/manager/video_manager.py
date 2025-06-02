import pygame
from pathlib import Path
from utils.config import PATHS
from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from pyvidplayer2 import Video

class VideoManager:
    def __init__(self):
        self.video = None
        self.is_playing = False
        
    def load_video(self, video_name):
        """Load video file by name"""
        video_path = PATHS['videos'] / f"{video_name}.mp4"
        
        try:
            self.video = Video(str(video_path))
            self.is_playing = True
            return True
        except Exception as e:
            print(f"Error loading video: {e}")
            return False

    def update(self):
        """Check if video is still playing"""
        if not self.is_playing or not self.video:
            return False
        return True

    def stop(self):
        """Stop video playback"""
        if self.video:
            self.video.close()
        self.is_playing = False
        self.video = None
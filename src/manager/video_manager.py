import cv2
import requests
import numpy as np
import pygame
from pathlib import Path
import os

class VideoManager:
    def __init__(self):
        self.video = None
        self.fps = 0
        self.frame_delay = 0
        self.total_frames = 0
        self.is_playing = False
        self.last_frame_time = 0
        
        # Video sources (add your gofile links here)
        self.video_sources = {
            'intro': 'https://gofile.io/d/KXAt1V/prelude_cutscene.mp4',
            'ending': ''
        }

    def ensure_video_exists(self, video_name):
        """Check if video exists, download if not"""
        video_dir = Path("assets/video/cutscenes")
        video_path = video_dir / f"{video_name}.mp4"
        
        if not video_path.exists():
            print(f"Video {video_name} not found. Downloading...")
            video_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                response = requests.get(self.video_sources[video_name], stream=True)
                response.raise_for_status()
                
                with open(video_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        
                print(f"Downloaded {video_name}.mp4 successfully")
            except Exception as e:
                print(f"Error downloading video: {e}")
                return False
                
        return True

    def load_video(self, video_name):
        """Load video file by name"""
        if not self.ensure_video_exists(video_name):
            return False
            
        video_path = Path("assets/video/cutscenes") / f"{video_name}.mp4"
        
        try:
            self.video = cv2.VideoCapture(str(video_path))
            if not self.video.isOpened():
                raise Exception("Could not open video file")
            
            # Get video properties
            self.fps = self.video.get(cv2.CAP_PROP_FPS)
            self.frame_delay = 1000 / self.fps
            self.total_frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
            self.is_playing = True
            self.last_frame_time = pygame.time.get_ticks()
            return True
        except Exception as e:
            print(f"Error loading video: {e}")
            return False

    def update(self, surface):
        """Update video playback and render to surface"""
        if not self.is_playing:
            return False

        current_time = pygame.time.get_ticks()
        if current_time - self.last_frame_time >= self.frame_delay:
            ret, frame = self.video.read()
            if ret:
                # Convert frame to pygame surface
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, surface.get_size())
                frame = np.rot90(frame)
                frame = pygame.surfarray.make_surface(frame)
                surface.blit(frame, (0, 0))
                self.last_frame_time = current_time
                return True
            else:
                # Video finished
                self.stop()
                return False
        return True

    def stop(self):
        """Stop video playback and release resources"""
        self.is_playing = False
        if self.video:
            self.video.release()
            self.video = None
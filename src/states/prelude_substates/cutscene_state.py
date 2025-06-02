import pygame
from constants import *
from manager.video_manager import VideoManager
from pygame.locals import DOUBLEBUF

class CutsceneState:
    def __init__(self, surface):
        self.surface = surface
        self.video_manager = VideoManager()
        self.initialized = False

    def enter(self, video_name='prelude'):
        """Start playing the specified video"""
        if not self.initialized:
            if self.video_manager.load_video(video_name):
                self.initialized = True
                print('loaded')
            else:
                print('failed')
                return STATE_GAME
        return None
    
    def render(self, surface):
        """Add render method for video display"""
        if self.video_manager.is_playing:
            frame = self.video_manager.get_current_frame()
            if frame:
                surface.blit(frame, (0, 0))

    def update(self):
        """Update video playback"""
        if not self.initialized:
            return STATE_GAME
            
        if not self.video_manager.update():
            return STATE_GAME
        return None

    def handle_event(self, event):
        """Handle input events"""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_ESCAPE]:
                self.video_manager.stop()
                return STATE_GAME
        return None

    def exit(self):
        """Clean up resources"""
        self.video_manager.stop()
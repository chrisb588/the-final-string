from dotenv import load_dotenv
import os
import sys

# Load environment variables first
load_dotenv()

# Add the path to sys.path so Python can find modules
pythonpath = os.environ.get('PYTHONPATH')
if pythonpath and pythonpath not in sys.path:
    sys.path.insert(0, pythonpath)

import pygame
from constants import *

class PreludeState:
    def __init__(self):
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.cutscene_start = 0
        self.cutscene_length = 30000  # 30 seconds, adjust as needed
        self.scenes = []  # Will hold scene definitions
        self.current_scene = 0
        self.initialized = False
        
    def enter(self):
        """Called when entering the prelude state"""
        self.cutscene_start = pygame.time.get_ticks()
        self.initialized = False
        self.setup_scenes()
        
    def setup_scenes(self):
        """Define your cutscene scenes here"""
        self.scenes = [
            {
                'duration': 5000,  # Duration in milliseconds
                'render': self.render_scene_1
            },
            {
                'duration': 5000,
                'render': self.render_scene_2
            },
            # Add more scenes as needed
        ]
        
    def render_scene_1(self, progress):
        """Render first scene - progress is 0.0 to 1.0"""
        self.surface.fill(BG_COLOR)
        # Add your scene rendering code here
        
    def render_scene_2(self, progress):
        """Render second scene - progress is 0.0 to 1.0"""
        self.surface.fill(BG_COLOR)
        # Add your scene rendering code here
        
    def update(self):
        """Update cutscene state"""
        if not self.initialized:
            self.initialized = True
            return None
            
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.cutscene_start
        
        # Check if cutscene is complete
        if elapsed >= self.cutscene_length:
            return STATE_GAME
            
        # Update current scene
        time_in_scenes = 0
        for i, scene in enumerate(self.scenes):
            if elapsed < time_in_scenes + scene['duration']:
                self.current_scene = i
                break
            time_in_scenes += scene['duration']
            
        return None
        
    def handle_event(self, event):
        """Handle input events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                return STATE_GAME  # Skip cutscene
        return None
        
    def render(self):
        """Render current scene"""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.cutscene_start
        
        # Calculate progress through current scene
        time_in_scenes = 0
        for i in range(self.current_scene):
            time_in_scenes += self.scenes[i]['duration']
            
        scene_progress = (elapsed - time_in_scenes) / self.scenes[self.current_scene]['duration']
        scene_progress = max(0.0, min(1.0, scene_progress))
        
        # Render current scene
        self.scenes[self.current_scene]['render'](scene_progress)
        
        # You might want to add "Press SPACE to skip" text
        if pygame.font.get_init():
            font = pygame.font.Font(None, 24)
            skip_text = font.render("Press SPACE to skip", True, (255, 255, 255))
            self.surface.blit(skip_text, (10, SCREEN_HEIGHT - 30))
            
        # Display the surface
        pygame.display.flip()
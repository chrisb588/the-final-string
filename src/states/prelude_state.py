from dotenv import load_dotenv
import os
import sys
import json
from pathlib import Path

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
        self.subtitles = []
        self.current_subtitle = 0
        self.subtitle_start = 0
        self.subtitle_font = pygame.font.Font(FONT_PATH, 32)
        self.skip_font = pygame.font.Font(FONT_PATH, 24)
        self.load_subtitles()
        
    def load_subtitles(self):
        """Load subtitles and their timings"""
        try:
            current_file = Path(__file__)
            main_dir = current_file.parent.parent.parent
            
            # Load subtitle text
            subtitles_file = main_dir / "assets" / "data" / "prelude-cutscene.txt"
            with open(subtitles_file, "r") as f:
                subtitle_lines = [line.strip() for line in f.readlines() if line.strip()]
                
            # Load subtitle timings
            timings_file = main_dir / "assets" / "data" / "prelude-timings.json"
            with open(timings_file, "r") as f:
                timings = json.load(f)
                
            # Combine subtitles and timings
            self.subtitles = [
                {
                    'text': text,
                    'duration': timings.get(str(i), 3000)  # Default 3 seconds if not specified
                }
                for i, text in enumerate(subtitle_lines)
            ]
            
        except FileNotFoundError:
            self.subtitles = [{'text': 'Error loading subtitles', 'duration': 3000}]

    def enter(self):
        """Called when entering the prelude state"""
        self.cutscene_start = pygame.time.get_ticks()
        self.subtitle_start = self.cutscene_start
        self.current_subtitle = 0
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

        # Update subtitle
        current_time = pygame.time.get_ticks()
        if self.current_subtitle < len(self.subtitles):
            elapsed = current_time - self.subtitle_start
            if elapsed >= self.subtitles[self.current_subtitle]['duration']:
                self.current_subtitle += 1
                self.subtitle_start = current_time
                
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
        
        # if pygame.font.get_init():
        #     font = pygame.font.Font(None, 24)
        #     skip_text = font.render("Press SPACE to skip", True, (255, 255, 255))
        #     self.surface.blit(skip_text, (10, SCREEN_HEIGHT - 30))

        # Render current subtitle
        if self.current_subtitle < len(self.subtitles):
            subtitle_text = self.subtitles[self.current_subtitle]['text']
            text_surface = self.subtitle_font.render(subtitle_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(centerx=SCREEN_WIDTH//2, 
                                            bottom=SCREEN_HEIGHT - 50)
            self.surface.blit(text_surface, text_rect)
            
        # Render skip text
        skip_text = self.skip_font.render("Press SPACE to skip", True, (200, 200, 200))
        skip_rect = skip_text.get_rect(topright=(SCREEN_WIDTH - 20, 20))
        self.surface.blit(skip_text, skip_rect)
        
        pygame.display.flip()
            
        # Display the surface
        pygame.display.flip()
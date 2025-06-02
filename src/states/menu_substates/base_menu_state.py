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

class BaseMenuState:
    def __init__(self, screen, terminal):
        self.screen = screen
        self.terminal = terminal
        # self.crt_filter = crt_filter
        # self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
    def enter(self):
        """Called when entering this state"""
        pass
        
    def exit(self):
        """Called when exiting this state"""
        pass
        
    def update(self):
        """Update logic"""
        self.terminal.update()
        
    def render(self):
        """Render the state"""
        self.surface.fill(BG_COLOR)
        self.terminal.render(self.surface, (20, SCREEN_HEIGHT - 150))
        self.crt_filter.render(self.surface)
        pygame.display.flip()
        
    def handle_event(self, event):
        """Handle input events, return new state if needed"""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return STATE_MENU
        return None
from dotenv import load_dotenv
import os
import sys

# Load environment variables first
load_dotenv()

# Add the path to sys.path so Python can find modules
pythonpath = os.environ.get('PYTHONPATH')
if pythonpath and pythonpath not in sys.path:
    sys.path.insert(0, pythonpath)

from .base_menu_state import BaseMenuState
from constants import *
import pygame

class SettingsState(BaseMenuState):
    def __init__(self, screen, terminal):
        super().__init__(screen, terminal)
        self.selected_item = 0
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return STATE_MENU
        return None
    
    def enter(self):
        """Display all menu text at once in terminal style"""
        self.terminal.clear()

        self.terminal.add_line("Press Esc to go back to main menu")
            
    def render(self):
        self.screen.fill(BG_COLOR)
        self.terminal.render(self.screen, (20, SCREEN_HEIGHT - 50))
        # self.crt_filter.render(self.screen)
        # pygame.display.flip()
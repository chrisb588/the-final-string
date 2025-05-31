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
    def __init__(self, screen, terminal, crt_filter):
        super().__init__(screen, terminal, crt_filter)
        self.menu_font = pygame.font.Font(FONT_PATH, MENU_FONT_SIZE)
        self.selected_setting = 0
        self.settings = ["Volume", "Screen Size", "Back"]
        
    def enter(self):
        self.terminal.add_line("> Settings")
        self.terminal.add_line("> Press ESC to return to main menu")
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_setting = (self.selected_setting - 1) % len(self.settings)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_setting = (self.selected_setting + 1) % len(self.settings)
            elif event.key == pygame.K_RETURN:
                if self.settings[self.selected_setting] == "Back":
                    return STATE_MENU
        return super().handle_event(event)
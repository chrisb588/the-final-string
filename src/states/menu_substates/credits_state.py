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

class CreditsState(BaseMenuState):
    def __init__(self, screen, terminal, crt_filter):
        super().__init__(screen, terminal, crt_filter)
        self.title_font = pygame.font.Font(FONT_PATH, TITLE_FONT_SIZE)
        self.menu_font = pygame.font.Font(FONT_PATH, MENU_FONT_SIZE)
        
    def enter(self):
        self.terminal.add_line("> Credits")
        self.terminal.add_line("> Press ESC to return to main menu")
        for creator in CREATORS:
            self.terminal.add_line(f"> {creator}")
        
    def render(self):
        self.surface.fill(BG_COLOR)
        
        # Draw title
        text = self.title_font.render("Credits", True, TERMINAL_GREEN)
        self.surface.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 100))
        
        # Draw creators
        for i, creator in enumerate(CREATORS):
            text = self.menu_font.render(creator, True, TERMINAL_GREEN)
            self.surface.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 250 + i * 60))
        
        # Draw terminal
        self.terminal.render(self.surface, (20, SCREEN_HEIGHT - 150))
        self.crt_filter.render(self.surface)
        pygame.display.flip()
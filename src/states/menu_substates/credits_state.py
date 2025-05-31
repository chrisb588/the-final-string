from dotenv import load_dotenv
import os
import sys
from pathlib import Path

# Load environment variables first
load_dotenv()

# Add the path to sys.path so Python can find modules
pythonpath = os.environ.get('PYTHONPATH')
if pythonpath and pythonpath not in sys.path:
    sys.path.insert(0, pythonpath)

from menu_substates.base_menu_state import BaseMenuState
from constants import *
import pygame

class CreditsState(BaseMenuState):
    def __init__(self, screen, terminal, crt_filter):
        super().__init__(screen, terminal, crt_filter)
        self.credits_lines = []
        self.current_page = 0
        self.lines_per_page = 15
        self.load_credits()
        
    def load_credits(self):
        """Load credits from file"""
        try:
            current_file = Path(__file__)
            main_dir = current_file.parent.parent.parent.parent
            credits_file = main_dir / "credits.txt"
            
            with open(credits_file, "r") as f:
                self.credits_lines = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            self.credits_lines = ["Credits file not found"]
            
    def get_total_pages(self):
        """Calculate total number of pages"""
        return max(1, (len(self.credits_lines) + self.lines_per_page - 1) // self.lines_per_page)
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return STATE_MENU
            elif event.key in (pygame.K_a, pygame.K_LEFT):
                self.current_page = max(0, self.current_page - 1)
                self.update_display()
            elif event.key in (pygame.K_d, pygame.K_RIGHT):
                self.current_page = min(self.get_total_pages() - 1, self.current_page + 1)
                self.update_display()
        return None
    
    def enter(self):
        """Display initial credits page"""
        self.current_page = 0
        self.update_display()
        
    def update_display(self):
        """Update terminal display for current page"""
        self.terminal.clear()
         
        # Calculate page content
        start_idx = self.current_page * self.lines_per_page
        end_idx = min(start_idx + self.lines_per_page, len(self.credits_lines))
        
        # Display current page content
        for line in self.credits_lines[start_idx:end_idx]:
            self.terminal.add_line(line)

        # Display page navigation info
        self.terminal.add_line("")
        self.terminal.add_line(f"Credits (Page {self.current_page + 1}/{self.get_total_pages()})")
        self.terminal.add_line("Use A/D or Arrow Left/Right to navigate pages")
        self.terminal.add_line("Press ESC to return to menu")
            
    def render(self):
        self.surface.fill(BG_COLOR)
        self.terminal.render(self.surface, (20, SCREEN_HEIGHT - 50))
        self.crt_filter.render(self.surface)
        pygame.display.flip()
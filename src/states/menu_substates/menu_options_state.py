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

class MenuOptionsState(BaseMenuState):
    def __init__(self, screen, terminal):
        super().__init__(screen, terminal)
        self.selected_item = 0
        self.transitioning = False
        self.transition_start = 0
        self.transition_delay = 5000  # 5 seconds in milliseconds
        self.title_font = pygame.font.Font(FONT_PATH, MENU_FONT_SIZE) # Create font for title
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                if self.selected_item > 0:  # Only move if not at top
                    self.selected_item -= 1
                    self._update_menu_items()
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                if self.selected_item < len(MENU_ITEMS) - 1:  # Only move if not at bottom
                    self.selected_item += 1
                    self._update_menu_items()
            elif event.key == pygame.K_RETURN:
                return self._handle_selection()
        return None
    
    def enter(self):
        """Display all menu text at once in terminal style"""
        self.terminal.clear()
        
        # Add ALL loading stages
        for stage in LOADING_STAGES:
            self.terminal.add_line(stage[0], animate_dots=False)
            
        # Define title lines
        title_line1 = "The Final String:"
        title_line2 = "Win By Making Better Passwords"

        # Add title lines
        self.terminal.add_line("") # Spacer
        self.terminal.add_line(
            title_line1, 
            color=TERMINAL_YELLOW, # Use yellow for the main part of the title
            font=self.title_font, 
            center=True
        )
        self.terminal.add_line("") # <<<<< Added this line for extra space
        self.terminal.add_line(
            title_line2,
            color=TERMINAL_GREEN, # Default terminal green for the subtitle
            # font=self.terminal.font, # Implicitly uses default terminal font if not specified
            center=True
        )
        self.terminal.add_line("") # Spacer
            
        self.terminal.add_line("Created by: " + ", ".join(CREATORS))
        self.terminal.add_line("")
        
        # Add menu items
        for i, item in enumerate(MENU_ITEMS):
            prefix = "> " if i == self.selected_item else "  "
            color = TERMINAL_YELLOW if i == self.selected_item else TERMINAL_GREEN
            self.terminal.add_line(prefix + item, color=color)
            
        self.terminal.add_line("")
        self.terminal.add_line(CONTROLS_TEXT)
    
    def _update_menu_items(self):
        """Update menu items to show current selection"""
        # Find where menu items start by looking for the first menu item
        menu_start = 0
        for i, line in enumerate(self.terminal.lines):
            if line["text"].strip() in MENU_ITEMS or line["text"].strip()[2:] in MENU_ITEMS:
                menu_start = i
                break
                
        # Update menu items
        for i, item in enumerate(MENU_ITEMS):
            if menu_start + i < len(self.terminal.lines):
                prefix = "> " if i == self.selected_item else "  "
                color = TERMINAL_YELLOW if i == self.selected_item else TERMINAL_GREEN
                self.terminal.lines[menu_start + i]["text"] = prefix + item
                self.terminal.lines[menu_start + i]["color"] = color
        
    def _handle_selection(self):
        selection = MENU_ITEMS[self.selected_item]
        if selection == "Play":
            # Clear terminal and show transition message
            self.terminal.clear()
            self.terminal.add_line("Running the-final-string.exe", color={
                "The Final String": TERMINAL_YELLOW
            }, animate_dots=True)
            self.transition_start = pygame.time.get_ticks()
            self.transitioning = True
            return None  # Don't transition immediately
        elif selection == "How To Play":
            return STATE_MENU_HOW_TO_PLAY
        elif selection == "Settings":
            return STATE_MENU_SETTINGS
        elif selection == "Credits":
            return STATE_MENU_CREDITS
        elif selection == "Exit":
            pygame.quit()
            sys.exit()

    def update(self):
        """Handle transition timing"""
        if self.transitioning:
            current_time = pygame.time.get_ticks()
            if current_time - self.transition_start >= self.transition_delay:
                self.transitioning = False
                return STATE_PRELUDE
        return None
            
    def render(self):
        self.screen.fill(BG_COLOR)
        self.terminal.render(self.screen, (20, SCREEN_HEIGHT - 250))
        # self.crt_filter.render(self.screen)
        # pygame.display.flip()
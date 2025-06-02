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

class HowToPlayState(BaseMenuState):
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

        self.terminal.add_line("How to play The Final String 101")
        self.terminal.add_line("")
        self.terminal.add_line("The Final String is a game where you create a password based from")
        self.terminal.add_line("a set of rules to progress through each level. Rules are scattered")
        self.terminal.add_line("across the level and can be known by interacting with certain objects")
        self.terminal.add_line("placed on the level. Enter a password that satisfies all the rules for")
        self.terminal.add_line("that level to move to the next level.")
        self.terminal.add_line("")
        self.terminal.add_line("CONTROLS:")
        self.terminal.add_line("")
        self.terminal.add_line("Press W/A/S/D to move up/left/down/right", color={
            "W": TERMINAL_YELLOW,
            "A": TERMINAL_YELLOW,
            "S": TERMINAL_YELLOW,
            "D": TERMINAL_YELLOW,
        })
        self.terminal.add_line("Alternatively, you can use the arrow keys to move", color={
            "arrow keys": TERMINAL_YELLOW
        })
        self.terminal.add_line("Press E to interact with objects and doors", color={
            "E": TERMINAL_YELLOW
        })
        self.terminal.add_line("Press Esc to pause the game or exit an interface", color={
            "Esc": TERMINAL_YELLOW
        })
        self.terminal.add_line("")
        self.terminal.add_line("Press Esc to go back to main menu")
            
    def render(self):
        self.screen.fill(BG_COLOR)
        self.terminal.render(self.screen, (20, SCREEN_HEIGHT - 50))
        # self.crt_filter.render(self.screen)
        # pygame.display.flip()
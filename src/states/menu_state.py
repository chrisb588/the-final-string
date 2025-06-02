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
from pygame.locals import DOUBLEBUF, OPENGL
from constants import *
from states.menu_substates.ui.crt_filter import CRTFilter
from states.menu_substates.ui.terminal import Terminal
from states.menu_substates.loading_menu_state import LoadingMenuState
from states.menu_substates.menu_options_state import MenuOptionsState
from states.menu_substates.how_to_play_state import HowToPlayState
from states.menu_substates.settings_state import SettingsState
from states.menu_substates.credits_state import CreditsState
from states.prelude_state import PreludeState

class Menu:
    def __init__(self, surface):
        self.screen = surface
        self.terminal = Terminal(pygame.font.Font(FONT_PATH, TERMINAL_FONT_SIZE))
        
        # Initialize all states with surface instead of screen
        self.states = {
            STATE_MENU_LOADING: LoadingMenuState(self.screen, self.terminal),
            STATE_MENU: MenuOptionsState(self.screen, self.terminal),
            STATE_MENU_HOW_TO_PLAY: HowToPlayState(self.screen, self.terminal),
            STATE_MENU_SETTINGS: SettingsState(self.screen, self.terminal),
            STATE_MENU_CREDITS: CreditsState(self.screen, self.terminal)
        }
        
        self.current_state = STATE_MENU_LOADING
        self.clock = pygame.time.Clock()

    def enter(self):
        """Called when entering the menu state"""
        self.states[self.current_state].enter()

    def exit(self):
        """Called when exiting the menu state"""
        self.states[self.current_state].exit()

    def run(self, event=None):
        """Run one frame of the menu state"""
        # Handle event if provided
        if event:
            next_state = self.states[self.current_state].handle_event(event)
            if next_state == STATE_PRELUDE:
                return 'prelude'
            elif next_state is not None:
                self.change_state(next_state)
        return None

    def update(self):
        """Update current menu state"""
        next_state = self.states[self.current_state].update()
        if next_state == STATE_PRELUDE:
            return 'prelude'
        elif next_state is not None:
            self.change_state(next_state)
        return None

    def render(self):
        """Render current menu state"""
        self.states[self.current_state].render()

    def change_state(self, new_state):
        """Handle internal menu state transitions"""
        if new_state in self.states:
            self.states[self.current_state].exit()
            self.current_state = new_state
            self.states[self.current_state].enter()

    def handle_event(self, event):
        """Handle events in the current menu state"""
        if hasattr(self.states[self.current_state], 'handle_event'):
            next_state = self.states[self.current_state].handle_event(event)
            if next_state == STATE_PRELUDE:
                return 'prelude'  # Return game state name
            elif next_state is not None:
                self.change_state(next_state)  # Handle internal menu state changes
        return None
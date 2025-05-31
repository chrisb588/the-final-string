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
from menu_substates.ui.crt_filter import CRTFilter
from menu_substates.ui.terminal import Terminal
from menu_substates.loading_menu_state import LoadingMenuState
from menu_substates.menu_options_state import MenuOptionsState
from menu_substates.how_to_play_state import HowToPlayState
from menu_substates.settings_state import SettingsState
from menu_substates.credits_state import CreditsState
from states.prelude_state import PreludeState

class Menu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 
                                            DOUBLEBUF | OPENGL)
        self.crt_filter = CRTFilter(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.terminal = Terminal(pygame.font.Font(FONT_PATH, TERMINAL_FONT_SIZE))
        
        # Initialize all states
        self.states = {
            STATE_LOADING: LoadingMenuState(self.screen, self.terminal, self.crt_filter),
            STATE_MENU: MenuOptionsState(self.screen, self.terminal, self.crt_filter),
            STATE_PRELUDE: PreludeState(),
            STATE_HOW_TO_PLAY: HowToPlayState(self.screen, self.terminal, self.crt_filter),
            STATE_SETTINGS: SettingsState(self.screen, self.terminal, self.crt_filter),
            STATE_CREDITS: CreditsState(self.screen, self.terminal, self.crt_filter)
        }
        
        self.current_state = STATE_LOADING
        self.states[self.current_state].enter()
        
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    continue
                
                # Let current state handle the event
                next_state = self.states[self.current_state].handle_event(event)
                if next_state is not None:
                    self.change_state(next_state)
            
            # Update current state
            next_state = self.states[self.current_state].update()
            if next_state is not None:
                self.change_state(next_state)
            
            # Render current state
            self.states[self.current_state].render()
            
            self.clock.tick(60)
        
        pygame.quit()
    
    def change_state(self, new_state):
        """Handle state transitions"""
        if new_state in self.states:
            self.states[self.current_state].exit()
            self.current_state = new_state
            self.states[self.current_state].enter()

if __name__ == "__main__":
    game = Menu()
    game.run()
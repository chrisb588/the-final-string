from dotenv import load_dotenv
import os
import sys
import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from states.menu_substates.ui.crt_filter import CRTFilter
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

# Load environment variables
# load_dotenv()

# # Add the path to sys.path
# pythonpath = os.environ.get('PYTHONPATH')
# if pythonpath and pythonpath not in sys.path:
#     sys.path.insert(0, pythonpath)

from states.menu_state import Menu
from states.game_state import GameDemo
from states.prelude_state import PreludeState
from states.end_state import EndState  # You'll need to create this

class Game:
    def __init__(self):
        pygame.init()
        self.is_fullscreen = False
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("The Final String")
        
        # Store original resolution for toggling
        self.windowed_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Create game surface for regular rendering
        self.game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Initialize CRT filter
        self.crt_filter = CRTFilter(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Initialize states with game_surface instead of screen
        menu = Menu(self.game_surface)
        prelude = PreludeState()
        end = EndState()
        
        self.states = {
            'menu': menu,
            'prelude': prelude,
            'end': end
        }
        
        self.current_state = 'menu'
        self.clock = pygame.time.Clock()
        self.running = True

    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            # Get the current display info
            display_info = pygame.display.Info()
            # Set to fullscreen at desktop resolution
            self.screen = pygame.display.set_mode(
                (display_info.current_w, display_info.current_h),
                DOUBLEBUF | OPENGL | pygame.FULLSCREEN
            )
        else:
            # Return to windowed mode
            self.screen = pygame.display.set_mode(
                self.windowed_size,
                DOUBLEBUF | OPENGL
            )
        
        # Reinitialize CRT filter for new resolution
        if self.is_fullscreen:
            display_info = pygame.display.Info()
            self.crt_filter = CRTFilter(display_info.current_w, display_info.current_h)
        else:
            self.crt_filter = CRTFilter(SCREEN_WIDTH, SCREEN_HEIGHT)

    def render_frame(self):
        """Handle the complete rendering pipeline"""
        # First render state to game surface
        if hasattr(self.states[self.current_state], 'render'):
            self.states[self.current_state].render()
        
        # Apply CRT filter effect
        self.crt_filter.render(self.game_surface)
        
        pygame.display.flip()

    def run(self):
        # Enter initial state
        if hasattr(self.states[self.current_state], 'enter'):
            self.states[self.current_state].enter()

        while self.running:
            # Clear the game surface
            self.game_surface.fill((0, 0, 0))
            
            # Handle global events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    continue
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()
                # Let current state handle events
                # if hasattr(self.states[self.current_state], 'run'):
                #     next_state = self.states[self.current_state].run(event)
                #     if next_state:
                #         self.change_state(next_state)
                # Handle menu-specific events
                if self.current_state == 'menu':
                    if hasattr(self.states[self.current_state], 'handle_event'):
                        next_state = self.states[self.current_state].handle_event(event)
                        if next_state:
                            self.change_state(next_state)
            
            # Run a frame without events
            if hasattr(self.states[self.current_state], 'run'):
                self.states[self.current_state].run()

            # Update current state
            if hasattr(self.states[self.current_state], 'update'):
                next_state = self.states[self.current_state].update()
                if next_state:
                    self.change_state(next_state)
           
            
            self.render_frame()
            self.clock.tick(60)
        
        # Exit final state
        if hasattr(self.states[self.current_state], 'exit'):
            self.states[self.current_state].exit()
        
        pygame.quit()
        sys.exit()

    def change_state(self, new_state):
        """Handle state transitions"""
        if new_state in self.states:
            # Call exit on current state if it exists
            if hasattr(self.states[self.current_state], 'exit'):
                self.states[self.current_state].exit()
            
            self.current_state = new_state
            
            # Call enter on new state if it exists
            if hasattr(self.states[self.current_state], 'enter'):
                self.states[self.current_state].enter()

if __name__ == "__main__":
    game = Game()
    game.run()
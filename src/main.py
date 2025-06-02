import os
import sys
import pygame
from pygame.locals import DOUBLEBUF
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_PATH

from states.menu_state import Menu
from states.game_state import GameDemo
from states.prelude_state import PreludeState
from states.end_state import EndState
from pyvidplayer2 import Video

class Game:
    def __init__(self):
        pygame.init()
        self.is_fullscreen = False
        self.windowed_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Initialize single screen
        self.screen = pygame.display.set_mode(self.windowed_size, DOUBLEBUF)
        pygame.display.set_caption("The Final String")
        
        # Initialize states
        menu = Menu(self.screen)
        prelude = PreludeState(self.screen)
        end = EndState()
        
        self.states = {
            'menu': menu,
            'prelude': prelude,
            'end': end
        }
        
        self.current_state = 'menu'
        self.clock = pygame.time.Clock()
        self.running = True
        self.vid1 = None  # Initialize video as None
        self.skip_font = pygame.font.Font(FONT_PATH, 24)

    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            display_info = pygame.display.Info()
            self.screen = pygame.display.set_mode(
                (display_info.current_w, display_info.current_h),
                DOUBLEBUF | pygame.FULLSCREEN
            )
        else:
            self.screen = pygame.display.set_mode(
                self.windowed_size,
                DOUBLEBUF
            )

    def render_frame(self):
        """Handle the complete rendering pipeline"""
        if self.current_state == 'prelude':
            # Only render video in prelude state
            pygame.time.wait(16)
            self.vid1.draw(self.screen, (0,0), force_draw=False)
            skip_text = self.skip_font.render("Press SPACE to skip", True, (200, 200, 200))
            skip_rect = skip_text.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
            self.screen.blit(skip_text, skip_rect)
            pygame.display.flip()
        else:
            # Render other states normally
            self.screen.fill((0, 0, 0))
            if hasattr(self.states[self.current_state], 'render'):
                self.states[self.current_state].render()
            pygame.display.flip()

    def run(self):
        # Enter initial state
        if hasattr(self.states[self.current_state], 'enter'):
            self.states[self.current_state].enter()

        while self.running:
            # Handle global events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    continue

                if self.current_state == 'prelude' and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.vid1.close()
                        self.change_state('game')  # Skip to game state
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()
                
                # Handle state-specific events
                if hasattr(self.states[self.current_state], 'handle_event'):
                    next_state = self.states[self.current_state].handle_event(event)
                    if next_state:
                        self.change_state(next_state)

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
            # Clean up previous state
            if hasattr(self.states[self.current_state], 'exit'):
                self.states[self.current_state].exit()
            
            # Handle video initialization/cleanup
            if new_state == 'prelude':
                self.vid1 = Video('assets/video/cutscenes/prelude.mp4')
            elif self.current_state == 'prelude':
                if self.vid1:
                    self.vid1.close()
                    self.vid1 = None
            
            self.current_state = new_state
            
            if hasattr(self.states[self.current_state], 'enter'):
                self.states[self.current_state].enter()

if __name__ == "__main__":
    game = Game()
    game.run()
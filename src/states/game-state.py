import pygame
from constants import *

class GameState:
    def __init__(self):
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
    def enter(self):
        pass
        
    def exit(self):
        pass
        
    def update(self):
        return None
        
    def handle_event(self, event):
        return None
        
    def render(self):
        self.surface.fill(BG_COLOR)
        # Add your game rendering code here
        pygame.display.flip()
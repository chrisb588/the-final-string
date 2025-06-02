from .base_menu_state import BaseMenuState
from constants import *
import pygame

class LoadingMenuState(BaseMenuState):
    def __init__(self, screen, terminal):
        super().__init__(screen, terminal)
        self.current_stage = -1
        self.stage_start_time = pygame.time.get_ticks()
        # Start first stage immediately
        self.advance_stage()

    def update(self):
        """Update loading state"""
        super().update()
        current_time = pygame.time.get_ticks()
        
        # Check if it's time for next stage
        if current_time - self.stage_start_time > LOADING_DELAY:
            return self.advance_stage()
            
        return None
        
    def advance_stage(self):
        """Advance to next loading stage"""
        self.current_stage += 1
        
        # Check if we've completed all stages
        if self.current_stage >= len(LOADING_STAGES):
            return STATE_MENU
            
        # Clear and rebuild all lines
        self.terminal.clear()
        
        # Add all previous stages without animation
        for stage in LOADING_STAGES[:self.current_stage]:
            self.terminal.lines.append({
                "text": stage[0],
                "animate_dots": False
            })
            
        # Add current stage with animation
        self.terminal.lines.append({
            "text": LOADING_STAGES[self.current_stage][0],
            "animate_dots": True
        })
        
        self.stage_start_time = pygame.time.get_ticks()
        return None

    def render(self):
        """Render the loading state"""
        self.screen.fill(BG_COLOR)
        self.terminal.render(self.screen, (20, SCREEN_HEIGHT - 50))
        # self.crt_filter.render(self.screen)
        # pygame.display.flip()
import pygame
import os

class PauseButton:
    """Manages the pause button functionality"""
    
    def __init__(self, screen):
        self.screen = screen
        self.paused = False
        self._init_font()

    def _init_font(self):
        """Initialize font with fallback"""
        try:
            # Get the current file's directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Navigate to the main directory (4 levels up from current file)
            main_dir = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
            
            # Construct path to font in assets directory
            font_path = os.path.join(main_dir, 'assets', 'fonts', 'UnifontEX.ttf')
            
            # Load font with error handling
            if os.path.exists(font_path):
                self.font = pygame.font.Font(font_path, 32)
            else:
                print(f"Warning: Font file not found at {font_path}")
                self.font = pygame.font.Font(None, 32)
        except (pygame.error, IOError) as e:
            print(f"Warning: Could not initialize font: {e}")
            self.font = pygame.font.SysFont('arial', 32)
        
    def toggle(self):
        """Toggle pause state"""
        self.paused = not self.paused
        return self.paused
        
    def is_paused(self) -> bool:
        """Check if game is paused"""
        return self.paused
        
    def draw(self, paused: bool = None):
        """Draw pause indicator when game is paused"""
        # Use passed parameter if provided, otherwise use internal state
        is_paused = paused if paused is not None else self.paused
        
        if not is_paused:
            return
            
        # Draw semi-transparent overlay
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Draw pause text
        pause_text = "PAUSED"
        text_surface = self.font.render(pause_text, True, (255, 255, 255))
        outline_surface = self.font.render(pause_text, True, (0, 0, 0))
        
        x = (self.screen.get_width() - text_surface.get_width()) // 2
        y = (self.screen.get_height() - text_surface.get_height()) // 2
        
        self.screen.blit(outline_surface, (x + 2, y + 2))
        self.screen.blit(text_surface, (x, y))
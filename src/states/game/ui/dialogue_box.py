import pygame
import os

class DialogueBox:
    """UI for displaying temporary messages"""
    
    def __init__(self, screen: pygame.Surface, ui_manager=None):
        self.screen = screen
        self.ui_manager = ui_manager
        self.message = ""
        self.show_until = 0
        self._init_font()
        
    def _init_font(self):
        """Initialize font with fallback"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            main_dir = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
            font_path = os.path.join(main_dir, 'assets', 'fonts', 'UnifontEX.ttf')
            
            if os.path.exists(font_path):
                self.font = pygame.font.Font(font_path, 24)
                print("Successfully loaded custom font for MessageUI: UnifontEX.ttf")
            else:
                print(f"Warning: Font file not found at {font_path}")
                self.font = pygame.font.Font(None, 24)
        except Exception as e:
            print(f"Warning: Could not initialize MessageUI font: {e}")
            self.font = pygame.font.Font(None, 24)
            
    def show_message(self, message: str, duration: int = 2000):
        """Show a message for the specified duration (milliseconds)"""
        self.message = message
        self.show_until = pygame.time.get_ticks() + duration
        
    def update(self):
        """Update message visibility"""
        if pygame.time.get_ticks() > self.show_until:
            self.message = ""
            
    def render(self):
        """Render the message if active"""
        if not self.message:
            return
            
        # Create text surface with outline
        text_surface = self.font.render(self.message, True, (255, 255, 255))
        outline_surface = self.font.render(self.message, True, (0, 0, 0))
        
        # Calculate position (centered, near bottom of screen)
        x = (self.screen.get_width() - text_surface.get_width()) // 2
        y = self.screen.get_height() - 100
        
        # Draw outline and text
        self.screen.blit(outline_surface, (x + 1, y + 1))
        self.screen.blit(text_surface, (x, y))
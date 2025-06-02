import pygame
import os

class RulesCount:    
    """UI for displaying collected rules count"""
    
    def __init__(self, screen: pygame.Surface, ui_manager=None):
        self.screen = screen
        self.ui_manager = ui_manager
        self._init_font()
        
    def _init_font(self):
        """Initialize font with fallback"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            main_dir = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
            font_path = os.path.join(main_dir, 'assets', 'fonts', 'UnifontEX.ttf')
            
            if os.path.exists(font_path):
                self.font = pygame.font.Font(font_path, 20)  # Increased size for better visibility
                print("Successfully loaded custom font for RulesCount: UnifontEX.ttf")
            else:
                print(f"Warning: Font file not found at {font_path}")
                self.font = pygame.font.Font(None, 20)
        except (pygame.error, IOError) as e:
            print(f"Warning: Could not initialize font: {e}")
            self.font = pygame.font.SysFont('arial', 20)
        
    def render(self, rules: list[str], total_rules: int = None):
        """Render the rules count display"""
        # Use total_rules if provided, otherwise use length of rules list
        max_rules = total_rules if total_rules is not None else len(rules)
        current_rules = len(rules)
        
        # Position in top-left corner
        x = 15
        y = 15
        padding = 8
        
        # Colors
        text_color = (230, 230, 240)
        bg_color = (45, 45, 55, 200)
        border_color = (80, 80, 90)
        
        # Create text
        text_content = f"Rules Found: {current_rules}/{max_rules}"
        text_surface = self.font.render(text_content, True, text_color)
        
        # Calculate dimensions
        width = text_surface.get_width() + padding * 2
        height = text_surface.get_height() + padding * 2
        
        # Draw background panel
        bg_rect = pygame.Rect(x - padding, y - padding, width, height)
        pygame.draw.rect(self.screen, bg_color, bg_rect, border_radius=5)
        pygame.draw.rect(self.screen, border_color, bg_rect, 1, border_radius=5)
        
        # Draw text
        self.screen.blit(text_surface, (x, y))
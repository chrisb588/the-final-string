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
import os
from constants import UI_COLORS, UI_DIMENSIONS, UI_ANIMATION, UI_FONT_SIZES, UI_ALPHA

class DialogueBox:
    """UI for displaying messages in a dialog box with typewriter effect"""
    
    def __init__(self, screen: pygame.Surface, ui_manager=None):
        self.screen = screen
        self.ui_manager = ui_manager
        self.message = ""
        self.displayed_message = ""  # Current displayed portion of message
        self.is_active = False
        self.char_index = 0
        self.last_char_time = 0
        self.char_delay = 30
        self.triangle_scale = 1.5
        self.scale_direction = 1
        self.typing_complete = False
        self._init_font()
        self._init_dimensions()
        
    def _init_font(self):
        """Initialize fonts with fallback"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            main_dir = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
            font_path = os.path.join(main_dir, 'assets', 'fonts', 'UnifontEX.ttf')
            
            if os.path.exists(font_path):
                self.font = pygame.font.Font(font_path, 24)
                self.small_font = pygame.font.Font(font_path, 16)  # Smaller font for exit text
                print("Successfully loaded custom font for DialogueBox")
            else:
                print(f"Warning: Font file not found at {font_path}")
                self.font = pygame.font.Font(None, 24)
                self.small_font = pygame.font.Font(None, 16)
        except Exception as e:
            print(f"Warning: Could not initialize DialogueBox font: {e}")
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 16)
            
    def _init_dimensions(self):
        """Initialize dialog box dimensions"""
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # Add horizontal padding (10% of screen width on each side)
        self.horizontal_padding = int(screen_width * 0.05)
        self.bottom_padding = 10
        self.box_height = UI_DIMENSIONS['DIALOG_HEIGHT']
        self.box_y = screen_height - self.box_height - self.bottom_padding
        self.padding = 20
        
    def show_message(self, message: str, duration: int = None):
        """Show a message in the dialog box"""
        self.message = message
        self.displayed_message = ""
        self.char_index = 0
        self.is_active = True
        self.typing_complete = False
        self.last_char_time = pygame.time.get_ticks()
            
    def update(self):
        """Update dialog box state"""
        if not self.is_active:
            return
            
        current_time = pygame.time.get_ticks()
        
        # Update typewriter effect
        if not self.typing_complete:
            if current_time - self.last_char_time >= self.char_delay:
                if self.char_index < len(self.message):
                    self.displayed_message += self.message[self.char_index]
                    self.char_index += 1
                    self.last_char_time = current_time
                else:
                    self.typing_complete = True
        
        # Update triangle animation
        if self.typing_complete:
            self.triangle_scale += 0.02 * self.scale_direction
            if self.triangle_scale >= 1.1:
                self.scale_direction = -1
            elif self.triangle_scale <= 0.9:
                self.scale_direction = 1
        
        # Handle exit key
        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_e] and self.typing_complete:
        #     self.hide()
            
    def hide(self):
        """Hide the dialog box"""
        self.is_active = False
        self.message = ""
        self.displayed_message = ""
        self.typing_complete = False
            
    def render(self):
        """Render the dialog box and message"""
        if not self.is_active:
            return
            
        # Draw dialog box background
        screen_width = self.screen.get_width()
        box_width = screen_width - (self.horizontal_padding * 2)
        box_rect = pygame.Rect(
            self.horizontal_padding, 
            self.box_y, 
            box_width, 
            self.box_height
        )
        
        # Semi-transparent background (matching RulesCount colors)
        s = pygame.Surface((box_width, self.box_height))
        s.set_alpha(245)
        s.fill((45, 45, 55))
        self.screen.blit(s, (self.horizontal_padding, self.box_y))
        
        pygame.draw.rect(self.screen, (80, 80, 90), box_rect, 2, border_radius=5)
        
        # Render message with word wrap
        wrapped_text = self._wrap_text(
            self.displayed_message, 
            box_width - self.padding * 2
        )
        y_offset = self.box_y + self.padding
        
        for line in wrapped_text:
            text_surface = self.font.render(line, True, (230, 230, 240)) # Match RulesCount text color
            self.screen.blit(text_surface, (self.horizontal_padding + self.padding, y_offset))
            y_offset += self.font.get_linesize()
        
        # Draw exit prompt and triangle when typing is complete
        if self.typing_complete:
            # Draw "Press E to exit" text
            exit_text = self.small_font.render("Press E to exit", True, (230, 230, 240))
            exit_text_rect = exit_text.get_rect()
            exit_text_pos = (
                screen_width - self.horizontal_padding - self.padding - exit_text_rect.width - 20,
                self.box_y + self.box_height - self.padding - exit_text_rect.height
            )
            self.screen.blit(exit_text, exit_text_pos)
            
            # Draw inverted triangle
            base_size = 12  # Base triangle size
            scaled_size = base_size * self.triangle_scale  # Scale uniformly
            
            triangle_x = screen_width - self.horizontal_padding - self.padding - scaled_size/2
            triangle_y = exit_text_pos[1] + exit_text_rect.height/2
            
            # Define triangle points (now pointing down)
            triangle_points = [
                (triangle_x - scaled_size/2, triangle_y - scaled_size/2),  # Top left
                (triangle_x + scaled_size/2, triangle_y - scaled_size/2),  # Top right
                (triangle_x, triangle_y + scaled_size/2),  # Bottom point
            ]
            
            pygame.draw.polygon(self.screen, (230, 230, 240), triangle_points)
    
    def complete_typing(self):
        """Skip typing animation and show complete message"""
        if not self.typing_complete:
            self.displayed_message = self.message
            self.char_index = len(self.message)
            self.typing_complete = True
            self.last_char_time = pygame.time.get_ticks()  

    def _wrap_text(self, text: str, max_width: int) -> list:
        """Wrap text to fit within specified width"""
        words = text.split(' ')
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            word_surface = self.font.render(word + ' ', True, (230, 230, 240))
            word_width = word_surface.get_width()
            
            if current_width + word_width > max_width:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width
            else:
                current_line.append(word)
                current_width += word_width
                
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for the dialog box"""
        if not self.is_active:
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                if not self.typing_complete:
                    self.complete_typing()
                    return True
                return False
                
        return False
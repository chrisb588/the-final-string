# UI component that keeps track of the no. of rules collectedclass RulesDisplayUI:

import pygame
import os
from ..utils.wrap_text import wrap_text
from ..utils.render_wrapped_text_lines import render_wrapped_text_lines

class RulesCount:    
    """UI for displaying collected rules in the corner"""
    
    def __init__(self, screen: pygame.Surface, ui_manager=None):
        self.screen = screen
        self.ui_manager = ui_manager

        self._init_font()
        
        # Minimize/maximize state
        self.is_minimized = False
        self.minimize_button_size = 20
        self.minimize_button_hovered = False
        self.minimize_button_rect = None  # Will be set during render

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
                self.font = pygame.font.Font(font_path, 16) # Adjusted size
                self.title_font = pygame.font.Font(font_path, 18) # Adjusted size
                print("Successfully loaded custom font for RulesDisplayUI: UnifontEX.ttf")
            else:
                print(f"Warning: Font file not found at {font_path}")
                self.font = pygame.font.Font(None, 16) # Adjusted size
                self.title_font = pygame.font.Font(None, 18) # Adjusted size
        except (pygame.error, IOError) as e:
            print(f"Warning: Could not initialize font: {e}")
            self.font = pygame.font.SysFont('arial', 16) # Adjusted size
            self.title_font = pygame.font.SysFont('arial', 18) # Adjusted size
        
    def handle_event(self, event):
        """Handle input events for the rules display"""
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            if self.minimize_button_rect:
                self.minimize_button_hovered = self.minimize_button_rect.collidepoint(mouse_pos)
            else:
                self.minimize_button_hovered = False
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.minimize_button_rect and self.minimize_button_rect.collidepoint(event.pos):
                self.is_minimized = not self.is_minimized
                return True  # Event was handled
                
        return False  # Event was not handled
        
    def render(self, rules: list[str]):
        """Render the rules display"""
        if not rules and not self.is_minimized:
            # Don't show anything if no rules and not minimized
            self.minimize_button_rect = None
            return
        
        text_color = self.ui_manager.text_color if self.ui_manager else (220,220,230)
        title_text_color = self.ui_manager.title_text_color if self.ui_manager else (230,230,240)
        bg_color = self.ui_manager.panel_bg_color if self.ui_manager else (45,45,55)
        border_color = self.ui_manager.panel_border_color if self.ui_manager else (80,80,90)
        
        # Position in top-left corner
        x = 15
        y = 15
        padding = 8
        
        # Draw title
        title_text_content = f"Current Level Rules ({len(rules)}):" if not self.is_minimized else f"Rules ({len(rules)})"
        title_surface = self.title_font.render(title_text_content, True, title_text_color)
        
        if self.is_minimized:
            # Minimized view - just show title and minimize button
            total_width = title_surface.get_width() + self.minimize_button_size + padding * 3
            total_height = max(title_surface.get_height(), self.minimize_button_size) + padding * 2
            
            # Draw background panel
            bg_rect = pygame.Rect(x - padding, y - padding, total_width, total_height)
            pygame.draw.rect(self.screen, bg_color, bg_rect, border_radius=5)
            pygame.draw.rect(self.screen, border_color, bg_rect, 1, border_radius=5)
            
            # Draw title
            self.screen.blit(title_surface, (x, y))
            
            # Draw maximize button (+)
            button_x = x + title_surface.get_width() + padding
            button_y = y + (title_surface.get_height() - self.minimize_button_size) // 2
            self.minimize_button_rect = pygame.Rect(button_x, button_y, self.minimize_button_size, self.minimize_button_size)
            
            button_color = (100, 200, 100) if self.minimize_button_hovered else (150, 150, 160)
            button_bg_color = (70, 80, 70) if self.minimize_button_hovered else (60, 60, 70)
            
            pygame.draw.rect(self.screen, button_bg_color, self.minimize_button_rect, border_radius=3)
            pygame.draw.rect(self.screen, button_color, self.minimize_button_rect, 2, border_radius=3)
            
            # Draw + symbol
            center_x = self.minimize_button_rect.centerx
            center_y = self.minimize_button_rect.centery
            offset = 6
            pygame.draw.line(self.screen, button_color, 
                            (center_x - offset, center_y), (center_x + offset, center_y), 2)
            pygame.draw.line(self.screen, button_color, 
                            (center_x, center_y - offset), (center_x, center_y + offset), 2)
            
        else:
            # Expanded view - show title, rules, and minimize button
            if not rules:
                self.minimize_button_rect = None
                return
                
            # Calculate max width for text wrapping (half screen width)
            max_text_width = self.screen.get_width() // 2 - padding * 4 - self.minimize_button_size
            
            # Wrap each rule text
            wrapped_rules = []
            for rule in rules:
                rule_text = f"• {rule}"
                wrapped_lines = wrap_text(rule_text, self.font, max_text_width)
                wrapped_rules.extend(wrapped_lines)
                wrapped_rules.append('')  # Add empty line between rules
            
            # Remove last empty line
            if wrapped_rules and wrapped_rules[-1] == '':
                wrapped_rules.pop()
            
            # Calculate dimensions based on wrapped text
            max_rule_width = max([self.font.size(line)[0] for line in wrapped_rules] + [0])
            content_width = max(title_surface.get_width(), max_rule_width)
            button_width = self.minimize_button_size + padding
            total_width = content_width + button_width + padding * 2
            
            # Calculate total height based on wrapped lines
            line_height = self.font.get_height()
            content_height = title_surface.get_height() + (len(wrapped_rules) * (line_height + 3)) # +3 for spacing
            total_height = content_height + padding * 2
            
            # Draw background panel
            bg_rect = pygame.Rect(x - padding, y - padding, total_width, total_height)
            pygame.draw.rect(self.screen, bg_color, bg_rect, border_radius=5)
            pygame.draw.rect(self.screen, border_color, bg_rect, 1, border_radius=5)
            
            # Draw minimize button (-)
            button_x = x + content_width + padding
            button_y = y
            self.minimize_button_rect = pygame.Rect(button_x, button_y, self.minimize_button_size, self.minimize_button_size)
            
            button_color = (200, 100, 100) if self.minimize_button_hovered else (150, 150, 160)
            button_bg_color = (80, 70, 70) if self.minimize_button_hovered else (60, 60, 70)
            
            pygame.draw.rect(self.screen, button_bg_color, self.minimize_button_rect, border_radius=3)
            pygame.draw.rect(self.screen, button_color, self.minimize_button_rect, 2, border_radius=3)
            
            # Draw - symbol
            center_x = self.minimize_button_rect.centerx
            center_y = self.minimize_button_rect.centery
            offset = 6
            pygame.draw.line(self.screen, button_color, 
                            (center_x - offset, center_y), (center_x + offset, center_y), 2)
            
            # Draw title
            self.screen.blit(title_surface, (x, y))
            
            # Draw wrapped rules
            current_y = y + title_surface.get_height() + 5 # Spacing after title
            render_wrapped_text_lines(self.screen, wrapped_rules, self.font, text_color, x, current_y, 3) 
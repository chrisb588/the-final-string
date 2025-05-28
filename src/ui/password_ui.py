import pygame
from typing import List, Dict, Optional, Callable

class PasswordUI:
    """UI for displaying password rules and handling password input"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 20)
        
        # UI state
        self.visible = False
        self.password_input = ""
        self.rules = []
        self.validation_results = {}
        self.message = ""
        self.door = None
        self.callback = None
        self.collected_rules = []
        
        # Colors
        self.bg_color = (0, 0, 0, 180)  # Semi-transparent black
        self.text_color = (255, 255, 255)
        self.rule_valid_color = (0, 255, 0)
        self.rule_invalid_color = (255, 0, 0)
        self.input_bg_color = (50, 50, 50)
        self.input_border_color = (100, 100, 100)
        
        # UI dimensions
        self.width = 600
        self.height = 400
        self.x = (screen.get_width() - self.width) // 2
        self.y = (screen.get_height() - self.height) // 2
        
    def show(self, rules: List[str], door, callback: Callable = None, collected_rules: List[str] = None):
        """Show the password UI with given rules"""
        self.visible = True
        self.rules = rules
        self.door = door
        self.callback = callback
        self.collected_rules = collected_rules or []
        self.password_input = ""
        self.validation_results = {}
        self.message = "Enter a password that follows all the rules:"
        
    def hide(self):
        """Hide the password UI"""
        self.visible = False
        self.password_input = ""
        self.validation_results = {}
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events. Returns True if event was consumed."""
        if not self.visible:
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.hide()
                return True
            elif event.key == pygame.K_RETURN:
                self._submit_password()
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.password_input = self.password_input[:-1]
                self._update_validation()
                return True
            else:
                # Add character to password input
                if event.unicode.isprintable():
                    self.password_input += event.unicode
                    self._update_validation()
                return True
        
        return False
    
    def _submit_password(self):
        """Submit the current password"""
        if self.door and self.callback:
            result = self.door.try_password(self.password_input)
            self.callback(result)
            
            if result.get("success", False):
                self.hide()
            else:
                self.message = result.get("message", "Incorrect password")
                self.validation_results = result.get("validation_results", {})
    
    def _update_validation(self):
        """Update real-time validation results"""
        if self.door:
            import sys
            import os
            # Add the src directory to the path so we can import game_state
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from game_state import game_state
            self.validation_results = game_state.validate_password_against_all_rules(self.password_input, self.rules)
    
    def render(self):
        """Render the password UI"""
        if not self.visible:
            return
            
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Draw main UI panel
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(self.screen, (40, 40, 40), panel_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), panel_rect, 2)
        
        # Draw title
        title_text = self.title_font.render("Password Required", True, self.text_color)
        title_x = self.x + (self.width - title_text.get_width()) // 2
        self.screen.blit(title_text, (title_x, self.y + 20))
        
        # Draw message
        message_text = self.font.render(self.message, True, self.text_color)
        message_x = self.x + (self.width - message_text.get_width()) // 2
        self.screen.blit(message_text, (message_x, self.y + 60))
        
        # Draw rules
        rules_y = self.y + 100
        for i, rule in enumerate(self.rules):
            # Determine rule color based on validation and whether it's collected
            if rule == "????":
                rule_color = (128, 128, 128)  # Gray for unknown rules
                status_symbol = "? "
            else:
                rule_color = self.text_color
                if rule in self.validation_results:
                    rule_color = self.rule_valid_color if self.validation_results[rule] else self.rule_invalid_color
                
                # Add checkmark or X
                status_symbol = ""
                if rule in self.validation_results:
                    status_symbol = "✓ " if self.validation_results[rule] else "✗ "
            
            rule_text = self.small_font.render(f"{status_symbol}{rule}", True, rule_color)
            self.screen.blit(rule_text, (self.x + 20, rules_y + i * 25))
        
        # Draw password input box
        input_y = rules_y + len(self.rules) * 25 + 20
        input_rect = pygame.Rect(self.x + 20, input_y, self.width - 40, 30)
        pygame.draw.rect(self.screen, self.input_bg_color, input_rect)
        pygame.draw.rect(self.screen, self.input_border_color, input_rect, 2)
        
        # Draw password input (visible)
        input_text = self.font.render(self.password_input, True, self.text_color)
        self.screen.blit(input_text, (input_rect.x + 5, input_rect.y + 5))
        
        # Draw cursor
        if pygame.time.get_ticks() % 1000 < 500:  # Blinking cursor
            cursor_x = input_rect.x + 5 + input_text.get_width()
            pygame.draw.line(self.screen, self.text_color, 
                           (cursor_x, input_rect.y + 5), 
                           (cursor_x, input_rect.y + 25), 2)
        
        # Draw instructions
        instructions = [
            "Type your password and press ENTER to submit",
            "Press ESC to cancel"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_text = self.small_font.render(instruction, True, (200, 200, 200))
            inst_x = self.x + (self.width - inst_text.get_width()) // 2
            self.screen.blit(inst_text, (inst_x, input_y + 50 + i * 20))

class MessageUI:
    """Simple UI for displaying temporary messages"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.messages = []  # List of (message, timestamp, duration)
        
    def show_message(self, message: str, duration: int = 3000):
        """Show a temporary message"""
        timestamp = pygame.time.get_ticks()
        self.messages.append((message, timestamp, duration))
        
    def update(self):
        """Update and remove expired messages"""
        current_time = pygame.time.get_ticks()
        self.messages = [(msg, ts, dur) for msg, ts, dur in self.messages 
                        if current_time - ts < dur]
    
    def render(self):
        """Render all active messages"""
        for i, (message, timestamp, duration) in enumerate(self.messages):
            # Calculate alpha based on remaining time
            current_time = pygame.time.get_ticks()
            elapsed = current_time - timestamp
            remaining = duration - elapsed
            
            if remaining > 0:
                alpha = min(255, remaining // 10)  # Fade out in last second
                
                # Render message
                text_surface = self.font.render(message, True, (255, 255, 255))
                text_surface.set_alpha(alpha)
                
                # Position message at middle bottom
                x = (self.screen.get_width() - text_surface.get_width()) // 2
                y = self.screen.get_height() - 100 - (len(self.messages) - i - 1) * 35
                
                # Draw background
                bg_rect = pygame.Rect(x - 5, y - 5, text_surface.get_width() + 10, text_surface.get_height() + 10)
                bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
                bg_surface.set_alpha(alpha // 2)
                bg_surface.fill((0, 0, 0))
                self.screen.blit(bg_surface, bg_rect)
                
                # Draw text
                self.screen.blit(text_surface, (x, y))

class RulesDisplayUI:
    """UI for displaying collected rules in the corner"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 18)
        self.title_font = pygame.font.Font(None, 20)
        
    def render(self, rules: List[str]):
        """Render the rules display"""
        if not rules:
            return
            
        # Position in top-left corner
        x = 10
        y = 10
        
        # Draw title
        title_text = self.title_font.render(f"Rules Found ({len(rules)}/4):", True, (255, 255, 255))
        
        # Draw background
        max_width = max(title_text.get_width(), 
                       max([self.font.size(rule)[0] for rule in rules] + [0]))
        height = 30 + len(rules) * 20
        
        bg_rect = pygame.Rect(x - 5, y - 5, max_width + 10, height)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(150)
        bg_surface.fill((0, 0, 0))
        self.screen.blit(bg_surface, bg_rect)
        
        # Draw title
        self.screen.blit(title_text, (x, y))
        
        # Draw rules
        for i, rule in enumerate(rules):
            rule_text = self.font.render(f"• {rule}", True, (200, 255, 200))
            self.screen.blit(rule_text, (x, y + 25 + i * 20)) 
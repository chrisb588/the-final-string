import pygame
import pyperclip  # For clipboard operations
from typing import List, Dict, Optional, Callable

class SelectableText:
    """A text widget that supports selection and clipboard operations with scrolling"""
    
    def __init__(self, text: str, font: pygame.font.Font, color: tuple, rect: pygame.Rect):
        self.text = text
        self.font = font
        self.default_color = color
        self.rect = rect
        self.lines = text.split('\n')
        self.line_height = font.get_height()
        self.line_colors = [color] * len(self.lines)  # Default all lines to same color
        
        # Selection state
        self.selection_start = None
        self.selection_end = None
        self.is_selecting = False
        
        # Scrolling state
        self.scroll_offset = 0
        self.max_visible_lines = max(1, self.rect.height // self.line_height)
        self.max_scroll = max(0, len(self.lines) - self.max_visible_lines)
        
    def set_line_colors(self, line_colors: List[tuple]):
        """Set colors for individual lines"""
        self.line_colors = line_colors
        # Ensure we have enough colors for all lines
        while len(self.line_colors) < len(self.lines):
            self.line_colors.append(self.default_color)
    
    def update_content(self, text: str):
        """Update the text content and recalculate scroll parameters"""
        self.text = text
        self.lines = text.split('\n')
        self.line_colors = [self.default_color] * len(self.lines)
        
        # Recalculate scroll parameters
        self.max_visible_lines = max(1, self.rect.height // self.line_height)
        self.max_scroll = max(0, len(self.lines) - self.max_visible_lines)
        
        # Auto-scroll to bottom if content is longer than visible area
        if self.max_scroll > 0:
            self.scroll_to_bottom()
    
    def scroll_to_bottom(self):
        """Scroll to the bottom of the content"""
        self.scroll_offset = self.max_scroll
    
    def scroll_to_top(self):
        """Scroll to the top of the content"""
        self.scroll_offset = 0
    
    def handle_scroll(self, scroll_direction: int):
        """Handle scroll wheel input"""
        old_offset = self.scroll_offset
        self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset + scroll_direction))
        return self.scroll_offset != old_offset  # Return True if scroll changed
        
    def handle_mouse_down(self, pos):
        """Handle mouse down for starting selection"""
        if self.rect.collidepoint(pos):
            self.selection_start = self._pos_to_char_index(pos)
            self.selection_end = self.selection_start
            self.is_selecting = True
            return True
        return False
    
    def handle_mouse_drag(self, pos):
        """Handle mouse drag for extending selection"""
        if self.is_selecting:
            self.selection_end = self._pos_to_char_index(pos)
            return True
        return False
    
    def handle_mouse_up(self, pos):
        """Handle mouse up for ending selection"""
        if self.is_selecting:
            self.is_selecting = False
            return True
        return False
    
    def _pos_to_char_index(self, pos):
        """Convert mouse position to character index in text"""
        rel_x = pos[0] - self.rect.x
        rel_y = pos[1] - self.rect.y
        
        # Account for scroll offset
        visible_line_index = rel_y // self.line_height
        actual_line_index = min(max(0, visible_line_index + self.scroll_offset), len(self.lines) - 1)
        
        if actual_line_index >= len(self.lines):
            return len(self.text)
        
        line = self.lines[actual_line_index]
        char_index = 0
        
        for i, char in enumerate(line):
            char_width = self.font.size(line[:i+1])[0]
            if char_width > rel_x:
                char_index = i
                break
            char_index = i + 1
        
        # Convert line-relative index to absolute index
        abs_index = sum(len(self.lines[i]) + 1 for i in range(actual_line_index)) + char_index
        return min(abs_index, len(self.text))
    
    def get_selected_text(self):
        """Get the currently selected text"""
        if self.selection_start is not None and self.selection_end is not None:
            start = min(self.selection_start, self.selection_end)
            end = max(self.selection_start, self.selection_end)
            return self.text[start:end]
        return ""
    
    def copy_selection(self):
        """Copy selected text to clipboard"""
        selected = self.get_selected_text()
        if selected:
            try:
                pyperclip.copy(selected)
                return True
            except:
                pass
        return False
    
    def render(self, screen):
        """Render the text with selection highlighting and scrolling"""
        # Calculate visible lines
        start_line = self.scroll_offset
        end_line = min(len(self.lines), start_line + self.max_visible_lines)
        
        y_offset = 0
        char_index = sum(len(self.lines[i]) + 1 for i in range(start_line))
        
        # Draw visible lines
        for line_idx in range(start_line, end_line):
            line = self.lines[line_idx]
            color = self.line_colors[line_idx] if line_idx < len(self.line_colors) else self.default_color
            line_surface = self.font.render(line, True, color)
            
            # Draw selection highlighting for this line
            if self.selection_start is not None and self.selection_end is not None:
                start = min(self.selection_start, self.selection_end)
                end = max(self.selection_start, self.selection_end)
                
                line_start = char_index
                line_end = char_index + len(line)
                
                if start < line_end and end > line_start:
                    # Calculate selection bounds within this line
                    sel_start_in_line = max(0, start - line_start)
                    sel_end_in_line = min(len(line), end - line_start)
                    
                    if sel_start_in_line < sel_end_in_line:
                        # Calculate pixel positions
                        start_x = self.font.size(line[:sel_start_in_line])[0] if sel_start_in_line > 0 else 0
                        end_x = self.font.size(line[:sel_end_in_line])[0]
                        
                        # Draw selection background
                        sel_rect = pygame.Rect(
                            self.rect.x + start_x,
                            self.rect.y + y_offset,
                            end_x - start_x,
                            self.line_height
                        )
                        pygame.draw.rect(screen, (100, 150, 255), sel_rect)
            
            # Draw the text
            screen.blit(line_surface, (self.rect.x, self.rect.y + y_offset))
            y_offset += self.line_height
            char_index += len(line) + 1  # +1 for newline
        
        # Draw scrollbar if needed
        if self.max_scroll > 0:
            self._draw_scrollbar(screen)
    
    def _draw_scrollbar(self, screen):
        """Draw a scrollbar on the right side"""
        scrollbar_width = 8
        scrollbar_x = self.rect.right - scrollbar_width
        scrollbar_y = self.rect.y
        scrollbar_height = self.rect.height
        
        # Draw scrollbar background
        scrollbar_bg = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        pygame.draw.rect(screen, (60, 60, 60), scrollbar_bg)
        
        # Draw scrollbar thumb
        if self.max_scroll > 0:
            thumb_height = max(20, int(scrollbar_height * self.max_visible_lines / len(self.lines)))
            thumb_y = scrollbar_y + int((scrollbar_height - thumb_height) * self.scroll_offset / self.max_scroll)
            thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
            pygame.draw.rect(screen, (120, 120, 120), thumb_rect)

class EditableText:
    """An editable text input that supports clipboard operations"""
    
    def __init__(self, font: pygame.font.Font, rect: pygame.Rect, initial_text: str = ""):
        self.font = font
        self.rect = rect
        self.text = initial_text
        self.cursor_pos = len(initial_text)
        self.selection_start = None
        self.selection_end = None
        self.focused = False
        
    def handle_event(self, event):
        """Handle input events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.focused = True
                self.cursor_pos = self._pos_to_cursor(event.pos)
                self.selection_start = None
                self.selection_end = None
                return True
            else:
                self.focused = False
                return False
        
        if not self.focused:
            return False
        
        if event.type == pygame.KEYDOWN:
            # Handle Ctrl combinations
            if event.mod & pygame.KMOD_CTRL:
                if event.key == pygame.K_c:  # Copy
                    self._copy_selection()
                    return True
                elif event.key == pygame.K_v:  # Paste
                    self._paste()
                    return True
                elif event.key == pygame.K_x:  # Cut
                    self._cut()
                    return True
                elif event.key == pygame.K_a:  # Select all
                    self.selection_start = 0
                    self.selection_end = len(self.text)
                    return True
            
            # Handle other keys
            if event.key == pygame.K_BACKSPACE:
                if self.selection_start is not None and self.selection_end is not None:
                    self._delete_selection()
                elif self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
                return True
            elif event.key == pygame.K_DELETE:
                if self.selection_start is not None and self.selection_end is not None:
                    self._delete_selection()
                elif self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
                return True
            elif event.key == pygame.K_LEFT:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
                self.selection_start = None
                self.selection_end = None
                return True
            elif event.key == pygame.K_RIGHT:
                if self.cursor_pos < len(self.text):
                    self.cursor_pos += 1
                self.selection_start = None
                self.selection_end = None
                return True
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
                self.selection_start = None
                self.selection_end = None
                return True
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.text)
                self.selection_start = None
                self.selection_end = None
                return True
            elif event.unicode and event.unicode.isprintable():
                if self.selection_start is not None and self.selection_end is not None:
                    self._delete_selection()
                self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                self.cursor_pos += 1
                return True
        
        return False
    
    def _pos_to_cursor(self, pos):
        """Convert mouse position to cursor position"""
        rel_x = pos[0] - self.rect.x
        for i in range(len(self.text) + 1):
            text_width = self.font.size(self.text[:i])[0]
            if text_width > rel_x:
                return i
        return len(self.text)
    
    def _copy_selection(self):
        """Copy selected text to clipboard"""
        if self.selection_start is not None and self.selection_end is not None:
            start = min(self.selection_start, self.selection_end)
            end = max(self.selection_start, self.selection_end)
            selected_text = self.text[start:end]
            try:
                pyperclip.copy(selected_text)
            except:
                pass
    
    def _paste(self):
        """Paste text from clipboard"""
        try:
            clipboard_text = pyperclip.paste()
            if clipboard_text:
                if self.selection_start is not None and self.selection_end is not None:
                    self._delete_selection()
                self.text = self.text[:self.cursor_pos] + clipboard_text + self.text[self.cursor_pos:]
                self.cursor_pos += len(clipboard_text)
        except:
            pass
    
    def _cut(self):
        """Cut selected text to clipboard"""
        if self.selection_start is not None and self.selection_end is not None:
            self._copy_selection()
            self._delete_selection()
    
    def _delete_selection(self):
        """Delete selected text"""
        if self.selection_start is not None and self.selection_end is not None:
            start = min(self.selection_start, self.selection_end)
            end = max(self.selection_start, self.selection_end)
            self.text = self.text[:start] + self.text[end:]
            self.cursor_pos = start
            self.selection_start = None
            self.selection_end = None
    
    def render(self, screen):
        """Render the text input"""
        # Draw background
        bg_color = (60, 60, 60) if self.focused else (40, 40, 40)
        border_color = (100, 150, 255) if self.focused else (100, 100, 100)
        
        pygame.draw.rect(screen, bg_color, self.rect)
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        # Draw selection
        if self.selection_start is not None and self.selection_end is not None:
            start = min(self.selection_start, self.selection_end)
            end = max(self.selection_start, self.selection_end)
            
            start_x = self.font.size(self.text[:start])[0]
            end_x = self.font.size(self.text[:end])[0]
            
            sel_rect = pygame.Rect(
                self.rect.x + 5 + start_x,
                self.rect.y + 5,
                end_x - start_x,
                self.rect.height - 10
            )
            pygame.draw.rect(screen, (100, 150, 255), sel_rect)
        
        # Draw text
        if self.text:
            text_surface = self.font.render(self.text, True, (255, 255, 255))
            screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        
        # Draw cursor
        if self.focused and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = self.rect.x + 5 + self.font.size(self.text[:self.cursor_pos])[0]
            pygame.draw.line(screen, (255, 255, 255), 
                           (cursor_x, self.rect.y + 5), 
                           (cursor_x, self.rect.y + self.rect.height - 5), 2)

class PasswordUI:
    """UI for displaying password rules and handling password input with text selection"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 20)
        
        # UI state
        self.visible = False
        self.rules = []
        self.validation_results = {}
        self.message = ""
        self.door = None
        self.callback = None
        self.collected_rules = []
        
        # UI dimensions
        self.width = 700
        self.height = 500
        self.x = (screen.get_width() - self.width) // 2
        self.y = (screen.get_height() - self.height) // 2
        
        # Text widgets
        self.rules_text = None
        self.password_input = None
        
    def show(self, rules: List[str], door, callback: Callable = None, collected_rules: List[str] = None, preserved_password: str = ""):
        """Show the password UI with given rules"""
        self.visible = True
        self.rules = rules
        self.door = door
        self.callback = callback
        self.collected_rules = collected_rules or []
        self.validation_results = {}
        self.message = "Enter a password that follows all the rules:"
        
        # Create rules text showing total required rules with collected/uncollected status
        rules_content = "Password Requirements:\n\n"
        
        # Get the total number of rules required (from door's required_rules)
        total_required = door.required_rules if door else len(rules)
        
        # Show all rule slots (collected + uncollected)
        for i in range(total_required):
            if i < len(self.collected_rules):
                # Show the actual collected rule
                rules_content += f"{i+1}. {self.collected_rules[i]}\n\n"
            else:
                # Show placeholder for uncollected rule
                rules_content += f"{i+1}. ????\n\n"
        
        rules_rect = pygame.Rect(self.x + 20, self.y + 80, self.width - 40, 250)
        
        # Update existing rules text or create new one
        if self.rules_text:
            self.rules_text.update_content(rules_content)
        else:
            self.rules_text = SelectableText(rules_content, self.small_font, (255, 255, 255), rules_rect)
            # Update scrolling parameters after content is set
            self.rules_text.max_visible_lines = max(1, self.rules_text.rect.height // self.rules_text.line_height)
            self.rules_text.max_scroll = max(0, len(self.rules_text.lines) - self.rules_text.max_visible_lines)
            # Auto-scroll to bottom if content is longer than visible area
            if self.rules_text.max_scroll > 0:
                self.rules_text.scroll_to_bottom()
        
        # Create password input with preserved password
        input_rect = pygame.Rect(self.x + 20, self.y + 350, self.width - 40, 30)
        self.password_input = EditableText(self.font, input_rect, preserved_password)
        
        # Auto-focus the password input so user can start typing immediately
        self.password_input.focused = True
        
        # Update validation immediately if we have a preserved password
        if preserved_password:
            self._update_validation()
        
    def hide(self):
        """Hide the password UI"""
        self.visible = False
        self.rules_text = None
        self.password_input = None
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events"""
        if not self.visible:
            return False
        
        # Handle global shortcuts
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.hide()
                return True
            elif event.key == pygame.K_RETURN:
                self._submit_password()
                return True
            elif event.mod & pygame.KMOD_CTRL and event.key == pygame.K_c:
                # Copy from rules text if it has selection
                if self.rules_text and self.rules_text.copy_selection():
                    return True
            # Handle keyboard scrolling for rules text (when password input is not focused)
            elif not (self.password_input and self.password_input.focused):
                if event.key == pygame.K_UP:
                    if self.rules_text and self.rules_text.handle_scroll(-1):
                        return True
                elif event.key == pygame.K_DOWN:
                    if self.rules_text and self.rules_text.handle_scroll(1):
                        return True
                elif event.key == pygame.K_PAGEUP:
                    if self.rules_text and self.rules_text.handle_scroll(-5):
                        return True
                elif event.key == pygame.K_PAGEDOWN:
                    if self.rules_text and self.rules_text.handle_scroll(5):
                        return True
                elif event.key == pygame.K_HOME:
                    if self.rules_text:
                        self.rules_text.scroll_to_top()
                        return True
                elif event.key == pygame.K_END:
                    if self.rules_text:
                        self.rules_text.scroll_to_bottom()
                        return True
        
        # Handle scroll wheel events for rules text
        if event.type == pygame.MOUSEWHEEL:
            if self.rules_text and self.rules_text.rect.collidepoint(pygame.mouse.get_pos()):
                # Scroll up (negative) or down (positive)
                scroll_direction = -event.y * 3  # Multiply by 3 for faster scrolling
                if self.rules_text.handle_scroll(scroll_direction):
                    return True
        
        # Handle mouse events for rules text
        if self.rules_text:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rules_text.handle_mouse_down(event.pos):
                    return True
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:  # Left button held
                    if self.rules_text.handle_mouse_drag(event.pos):
                        return True
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.rules_text.handle_mouse_up(event.pos):
                    return True
        
        # Handle password input events
        if self.password_input:
            if self.password_input.handle_event(event):
                self._update_validation()
                return True
        
        return False
    
    def _submit_password(self):
        """Submit the current password"""
        if self.door and self.callback and self.password_input:
            result = self.door.try_password(self.password_input.text)
            self.callback(result)
            
            if result.get("success", False):
                self.hide()
            else:
                self.message = result.get("message", "Incorrect password")
                self.validation_results = result.get("validation_results", {})
    
    def _update_validation(self):
        """Update real-time validation results"""
        if self.door and self.password_input:
            import sys
            import os
            # Add the src directory to the path so we can import game_state
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from game_state import game_state
            # Validate against collected rules only
            self.validation_results = game_state.validate_password_against_all_rules(self.password_input.text, self.collected_rules)
    
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
        title_text = self.title_font.render("Password Required", True, (255, 255, 255))
        title_x = self.x + (self.width - title_text.get_width()) // 2
        self.screen.blit(title_text, (title_x, self.y + 20))
        
        # Draw message
        message_text = self.font.render(self.message, True, (255, 255, 255))
        message_x = self.x + (self.width - message_text.get_width()) // 2
        self.screen.blit(message_text, (message_x, self.y + 60))
        
        # Update rules text colors based on validation
        if self.rules_text:
            line_colors = []
            for line in self.rules_text.lines:
                if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                    # This is a rule line
                    if "????" in line:
                        # Uncollected rule - show in gray
                        line_colors.append((150, 150, 150))
                    else:
                        # Collected rule - check if it's satisfied
                        rule_satisfied = False
                        if self.validation_results:
                            for rule, satisfied in self.validation_results.items():
                                if rule in line:
                                    rule_satisfied = satisfied
                                    break
                        
                        if rule_satisfied:
                            line_colors.append((0, 255, 0))  # Green for satisfied
                        else:
                            line_colors.append((255, 0, 0))  # Red for not satisfied
                else:
                    # Header or other text, keep white
                    line_colors.append((255, 255, 255))
            
            self.rules_text.set_line_colors(line_colors)
        
        # Render rules text (selectable with color coding)
        if self.rules_text:
            self.rules_text.render(self.screen)
        
        # Draw password input label
        input_label = self.font.render("Enter Password:", True, (255, 255, 255))
        self.screen.blit(input_label, (self.x + 20, self.y + 320))
        
        # Render password input (editable with clipboard support)
        if self.password_input:
            self.password_input.render(self.screen)
        
        # Draw validation results
        if self.password_input:
            valid_count = sum(1 for result in self.validation_results.values() if result) if self.validation_results else 0
            total_collected = len(self.collected_rules)
            total_required = self.door.required_rules if self.door else total_collected
            
            # Show both collected rules satisfaction and total progress
            validation_text = f"Rules satisfied: {valid_count}/{total_collected} | Total required: {total_collected}/{total_required}"
            validation_color = (0, 255, 0) if valid_count == total_collected and total_collected >= total_required else (255, 255, 0)
            validation_surface = self.small_font.render(validation_text, True, validation_color)
            self.screen.blit(validation_surface, (self.x + 20, self.y + 390))

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
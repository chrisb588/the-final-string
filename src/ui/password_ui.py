import pygame
import pyperclip  # For clipboard operations
from typing import List, Dict, Optional, Callable
import os

class SelectableText:
    """A text widget that supports selection and clipboard operations with scrolling"""
    
    def __init__(self, text: str, font: pygame.font.Font, color: tuple, rect: pygame.Rect, selection_bg_color: tuple = (80, 100, 150)):
        self.text = text
        self.font = font
        self.default_color = color
        self.rect = rect
        self.lines = text.split('\n')
        self.line_height = font.get_height()
        self.line_colors = [color] * len(self.lines)  # Default all lines to same color
        self.selection_bg_color = selection_bg_color
        
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
        
        text_padding_x = 10 # Added horizontal padding

        # Draw visible lines
        for line_idx in range(start_line, end_line):
            line = self.lines[line_idx]
            color = self.line_colors[line_idx] if line_idx < len(self.line_colors) else self.default_color
            line_surface = self.font.render(line, True, color)
            
            # Draw selection highlighting for this line
            if self.selection_start is not None and self.selection_end is not None:
                start = min(self.selection_start, self.selection_end)
                end = max(self.selection_start, self.selection_end)
                
                line_start_char_idx = sum(len(self.lines[i]) + 1 for i in range(line_idx)) # char index at start of this line
                
                if start < line_start_char_idx + len(line) and end > line_start_char_idx:
                    sel_start_in_line = max(0, start - line_start_char_idx)
                    sel_end_in_line = min(len(line), end - line_start_char_idx)
                    
                    if sel_start_in_line < sel_end_in_line:
                        start_x_offset = self.font.size(line[:sel_start_in_line])[0] if sel_start_in_line > 0 else 0
                        end_x_offset = self.font.size(line[:sel_end_in_line])[0]
                        
                        sel_rect = pygame.Rect(
                            self.rect.x + text_padding_x + start_x_offset,
                            self.rect.y + y_offset,
                            end_x_offset - start_x_offset,
                            self.line_height
                        )
                        pygame.draw.rect(screen, self.selection_bg_color, sel_rect)
            
            # Draw the text
            screen.blit(line_surface, (self.rect.x + text_padding_x, self.rect.y + y_offset))
            y_offset += self.line_height
        
        # Draw scrollbar if needed
        if self.max_scroll > 0:
            self._draw_scrollbar(screen)
    
    def _draw_scrollbar(self, screen):
        """Draw a scrollbar on the right side"""
        scrollbar_width = 6  # Made thinner
        scrollbar_margin = 2 # Margin from text
        scrollbar_x = self.rect.right - scrollbar_width - scrollbar_margin 
        scrollbar_y = self.rect.y
        scrollbar_height = self.rect.height
        
        # Draw scrollbar background
        scrollbar_bg = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        pygame.draw.rect(screen, self.ui_manager.scrollbar_bg_color, scrollbar_bg)
        
        # Draw scrollbar thumb
        if self.max_scroll > 0:
            thumb_height = max(20, int(scrollbar_height * self.max_visible_lines / len(self.lines)))
            thumb_y = scrollbar_y + int((scrollbar_height - thumb_height) * self.scroll_offset / self.max_scroll)
            thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
            pygame.draw.rect(screen, self.ui_manager.scrollbar_thumb_color, thumb_rect)

    def set_ui_manager(self, ui_manager):
        """Set the UI manager to access its color palette."""
        self.ui_manager = ui_manager

class EditableText:
    """An editable text input that supports clipboard operations"""
    
    def __init__(self, font: pygame.font.Font, rect: pygame.Rect, initial_text: str = "", ui_manager=None):
        self.font = font
        self.rect = rect
        self.text = initial_text
        self.cursor_pos = len(initial_text)
        self.selection_start = None
        self.selection_end = None
        self.focused = False
        self.ui_manager = ui_manager # Store reference to PasswordUI
        
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
        bg_color = self.ui_manager.input_bg_color if self.ui_manager else (60, 60, 70)
        border_color = self.ui_manager.input_focused_border_color if self.focused and self.ui_manager else (self.ui_manager.input_border_color if self.ui_manager else (100,100,110))
        text_color = self.ui_manager.text_color if self.ui_manager else (255,255,255)
        selection_bg_color = self.ui_manager.selection_bg_color if self.ui_manager else (80, 100, 150)
        
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=3)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=3)
        
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
            pygame.draw.rect(screen, selection_bg_color, sel_rect)
        
        # Draw text
        if self.text:
            text_surface = self.font.render(self.text, True, text_color)
            screen.blit(text_surface, (self.rect.x + 5, self.rect.y + (self.rect.height - text_surface.get_height()) // 2)) # Center text vertically
        
        # Draw cursor
        if self.focused and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = self.rect.x + 5 + self.font.size(self.text[:self.cursor_pos])[0]
            pygame.draw.line(screen, text_color, 
                           (cursor_x, self.rect.y + 5), 
                           (cursor_x, self.rect.y + self.rect.height - 5), 2)

class PasswordUI:
    """UI for displaying password rules and handling password input with text selection"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        
        # Load custom font from assets/fonts directory
        font_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "fonts", "Unifontexmono-2vrqo.ttf")
        
        try:
            self.font = pygame.font.Font(font_path, 22)  # Slightly smaller for better fit
            self.title_font = pygame.font.Font(font_path, 28) # Slightly smaller
            self.small_font = pygame.font.Font(font_path, 18) # Slightly smaller
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load custom font: {e}")
            print("Falling back to default font")
            # Fallback to default font if custom font fails to load
            self.font = pygame.font.Font(None, 24)
            self.title_font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 20)
        
        # Enhanced Color Palette
        self.panel_bg_color = (45, 45, 55)        # Darker blue-gray
        self.panel_border_color = (80, 80, 90)    # Lighter gray for border
        self.text_color = (220, 220, 230)         # Off-white/light lavender
        self.title_text_color = (230, 230, 240)   # Slightly brighter for title
        self.input_bg_color = (60, 60, 70)        # Darker input field
        self.input_border_color = (100, 100, 110) # Border for input
        self.input_focused_border_color = (120, 120, 220) # Highlight for focused input
        self.satisfied_rule_color = (100, 220, 100) # Softer green
        self.unsatisfied_rule_color = (220, 100, 100) # Softer red
        self.hidden_rule_color = (150, 150, 160)    # Gray for hidden rules
        self.message_color = (200, 200, 210)      # For messages
        self.scrollbar_bg_color = (60, 60, 70)
        self.scrollbar_thumb_color = (100, 100, 110)
        self.selection_bg_color = (80, 100, 150) # For text selection

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
            self.rules_text.set_ui_manager(self) # Ensure ui_manager is set
        else:
            self.rules_text = SelectableText(rules_content, self.small_font, self.text_color, rules_rect, self.selection_bg_color)
            self.rules_text.set_ui_manager(self) # Set ui_manager
            # Update scrolling parameters after content is set
            self.rules_text.max_visible_lines = max(1, self.rules_text.rect.height // self.rules_text.line_height)
            self.rules_text.max_scroll = max(0, len(self.rules_text.lines) - self.rules_text.max_visible_lines)
            # Auto-scroll to bottom if content is longer than visible area
            if self.rules_text.max_scroll > 0:
                self.rules_text.scroll_to_bottom()
        
        # Create password input with preserved password
        input_rect = pygame.Rect(self.x + 20, self.y + 350, self.width - 40, 35) # Increased height
        self.password_input = EditableText(self.font, input_rect, preserved_password, self)
        
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
        overlay.set_alpha(200) # Slightly more opaque
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        panel_padding = 20
        rules_rect_height = 230 # Adjusted height
        input_field_y_offset = 30 # Space between rules and input label
        input_label_to_field_offset = 5 # Space between input label and field
        validation_text_y_offset = 10 # Space between input field and validation

        # Draw main UI panel
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(self.screen, self.panel_bg_color, panel_rect, border_radius=10) # Added rounded corners
        pygame.draw.rect(self.screen, self.panel_border_color, panel_rect, 2, border_radius=10)
        
        # Draw title
        title_text = self.title_font.render("Password Required", True, self.title_text_color)
        title_x = self.x + (self.width - title_text.get_width()) // 2
        self.screen.blit(title_text, (title_x, self.y + panel_padding))
        
        # Draw message
        message_text_y = self.y + panel_padding + title_text.get_height() + 10
        message_text = self.font.render(self.message, True, self.message_color)
        message_x = self.x + (self.width - message_text.get_width()) // 2
        self.screen.blit(message_text, (message_x, message_text_y))
        
        rules_rect_y = message_text_y + message_text.get_height() + 15
        rules_rect = pygame.Rect(self.x + panel_padding, rules_rect_y, self.width - panel_padding*2, rules_rect_height)
        
        if self.rules_text:
            self.rules_text.rect = rules_rect # Update rect in case it changed
            line_colors = []
            for line in self.rules_text.lines:
                if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                    if "????" in line:
                        line_colors.append(self.hidden_rule_color)
                    else:
                        rule_satisfied = False
                        if self.validation_results:
                            for rule, satisfied in self.validation_results.items():
                                if rule in line:
                                    rule_satisfied = satisfied
                                    break
                        if rule_satisfied:
                            line_colors.append(self.satisfied_rule_color)
                        else:
                            line_colors.append(self.unsatisfied_rule_color)
                else:
                    line_colors.append(self.text_color)
            self.rules_text.set_line_colors(line_colors)
            self.rules_text.render(self.screen)
        
        input_label_y = rules_rect_y + rules_rect_height + input_field_y_offset
        input_label = self.font.render("Enter Password:", True, self.text_color)
        self.screen.blit(input_label, (self.x + panel_padding, input_label_y))
        
        input_field_y = input_label_y + input_label.get_height() + input_label_to_field_offset
        if self.password_input:
            self.password_input.rect.y = input_field_y # Update y position
            self.password_input.rect.x = self.x + panel_padding
            self.password_input.rect.width = self.width - panel_padding*2
            self.password_input.render(self.screen)
        
        validation_text_y = input_field_y + (self.password_input.rect.height if self.password_input else 35) + validation_text_y_offset
        if self.password_input:
            valid_count = sum(1 for result in self.validation_results.values() if result) if self.validation_results else 0
            total_collected = len(self.collected_rules)
            total_required = self.door.required_rules if self.door else total_collected
            validation_text = f"Rules satisfied: {valid_count}/{total_collected} | Total required: {total_collected}/{total_required}"
            validation_color = self.satisfied_rule_color if valid_count == total_collected and total_collected >= total_required and total_collected > 0 else self.unsatisfied_rule_color
            validation_surface = self.small_font.render(validation_text, True, validation_color)
            self.screen.blit(validation_surface, (self.x + panel_padding, validation_text_y))

class MessageUI:
    """Simple UI for displaying temporary messages"""
    
    def __init__(self, screen: pygame.Surface, ui_manager=None):
        self.screen = screen
        self.ui_manager = ui_manager
        
        # Load custom font from assets/fonts directory
        font_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "fonts", "Unifontexmono-2vrqo.ttf")
        
        try:
            self.font = pygame.font.Font(font_path, 20) # Adjusted size
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load custom font for MessageUI: {e}")
            # Fallback to default font if custom font fails to load
            self.font = pygame.font.Font(None, 22)
            
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
        text_color = self.ui_manager.text_color if self.ui_manager else (220,220,230)
        bg_color = self.ui_manager.panel_bg_color if self.ui_manager else (45,45,55)

        for i, (message, timestamp, duration) in enumerate(self.messages):
            # Calculate alpha based on remaining time
            current_time = pygame.time.get_ticks()
            elapsed = current_time - timestamp
            remaining = duration - elapsed
            
            if remaining > 0:
                alpha = min(255, int(255 * (remaining / duration))) # Smoother fade
                
                # Render message
                text_surface = self.font.render(message, True, text_color)
                text_surface.set_alpha(alpha)
                
                # Position message at middle bottom
                x = (self.screen.get_width() - text_surface.get_width()) // 2
                y = self.screen.get_height() - 60 - (len(self.messages) - i - 1) * 30 # Adjusted spacing
                
                # Draw background
                padding = 8
                bg_rect = pygame.Rect(x - padding, y - padding, text_surface.get_width() + padding*2, text_surface.get_height() + padding*2)
                pygame.draw.rect(self.screen, bg_color, bg_rect, border_radius=5) # Rounded corners
                pygame.draw.rect(self.screen, (0,0,0, alpha // 2), bg_rect, 1, border_radius=5) # Subtle border
                
                # Draw text
                self.screen.blit(text_surface, (x, y))

class RulesDisplayUI:
    """UI for displaying collected rules in the corner"""
    
    def __init__(self, screen: pygame.Surface, ui_manager=None):
        self.screen = screen
        self.ui_manager = ui_manager
        
        # Load custom font from assets/fonts directory
        font_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "fonts", "Unifontexmono-2vrqo.ttf")
        
        try:
            self.font = pygame.font.Font(font_path, 16) # Adjusted size
            self.title_font = pygame.font.Font(font_path, 18) # Adjusted size
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load custom font for RulesDisplayUI: {e}")
            # Fallback to default font if custom font fails to load
            self.font = pygame.font.Font(None, 18)
            self.title_font = pygame.font.Font(None, 20)

    def render(self, rules: List[str]):
        """Render the rules display"""
        if not rules:
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
        title_text_content = f"Rules Found ({len(rules)}):" # Removed /4 as it's dynamic
        title_surface = self.title_font.render(title_text_content, True, title_text_color)
        
        # Calculate dimensions
        max_rule_width = max([self.font.size(f"• {rule}")[0] for rule in rules] + [0])
        content_width = max(title_surface.get_width(), max_rule_width)
        total_width = content_width + padding * 2
        content_height = title_surface.get_height() + (len(rules) * (self.font.get_height() + 3)) # +3 for spacing
        total_height = content_height + padding * 2
        
        # Draw background panel
        bg_rect = pygame.Rect(x - padding, y - padding, total_width, total_height)
        pygame.draw.rect(self.screen, bg_color, bg_rect, border_radius=5)
        pygame.draw.rect(self.screen, border_color, bg_rect, 1, border_radius=5)
        
        # Draw title
        self.screen.blit(title_surface, (x, y))
        
        # Draw rules
        current_y = y + title_surface.get_height() + 5 # Spacing after title
        for rule in rules:
            rule_surface = self.font.render(f"• {rule}", True, text_color)
            self.screen.blit(rule_surface, (x, current_y))
            current_y += self.font.get_height() + 3 # Spacing between rules 
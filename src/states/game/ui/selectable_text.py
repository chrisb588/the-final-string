import pygame
import pyperclip

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
        
    def set_line_colors(self, line_colors: list[tuple]):
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
                # Clean up the selected text to remove unwanted LF characters
                # Replace single newlines with spaces for wrapped lines, but preserve paragraph breaks
                cleaned_text = self._clean_text_for_clipboard(selected)
                pyperclip.copy(cleaned_text)
                return True
            except:
                pass
        return False
    
    def _clean_text_for_clipboard(self, text: str) -> str:
        """Clean text for clipboard to avoid LF symbols and improve readability"""
        if not text:
            return text
        
        # Split into lines
        lines = text.split('\n')
        cleaned_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                # Empty line - preserve as paragraph break
                if cleaned_lines and cleaned_lines[-1] != '':
                    cleaned_lines.append('')
            else:
                # Check if this line is a continuation of a wrapped rule
                if (cleaned_lines and 
                    not line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', 'Password Requirements:', '•')) and
                    not line.endswith('????')):
                    # This is likely a wrapped continuation - join with previous line
                    if cleaned_lines:
                        cleaned_lines[-1] += ' ' + line
                else:
                    # This is a new rule or header - add as new line
                    cleaned_lines.append(line)
        
        # Join with proper line breaks
        result = '\n'.join(cleaned_lines)
        
        # Remove any remaining double spaces
        result = ' '.join(result.split())
        
        # Add back proper line breaks between rules
        result = result.replace('. ', '.\n').replace('Requirements:', 'Requirements:\n')
        
        return result
    
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
            self._draw_scrollbar(screen, self.max_visible_lines)
    
    def _draw_scrollbar(self, screen, visible_lines):
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
            thumb_height = max(20, int(scrollbar_height * visible_lines / len(self.lines)))
            thumb_y = scrollbar_y + int((scrollbar_height - thumb_height) * self.scroll_offset / self.max_scroll)
            
            # Clamp thumb_y and thumb_height to stay within scrollbar_bg
            thumb_y = max(scrollbar_y, min(thumb_y, scrollbar_y + scrollbar_height - thumb_height))
            if thumb_y + thumb_height > scrollbar_y + scrollbar_height:
                thumb_height = scrollbar_y + scrollbar_height - thumb_y
            
            thumb_color = self.ui_manager.scrollbar_thumb_color if self.ui_manager else (120, 120, 130)
            thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
            pygame.draw.rect(screen, thumb_color, thumb_rect)

    def set_ui_manager(self, ui_manager):
        """Set the UI manager to access its color palette."""
        self.ui_manager = ui_manager
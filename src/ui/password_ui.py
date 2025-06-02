import pygame
import pyperclip  # For clipboard operations
from typing import List, Dict, Optional, Callable
import os

def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> List[str]:
    """
    Wrap text to fit within max_width pixels
    
    Args:
        text: Text to wrap
        font: Font to use for measuring text width
        max_width: Maximum width in pixels
        
    Returns:
        List of wrapped lines
    """
    if not text.strip():
        return [text]
    
    # Handle explicit line breaks first
    paragraphs = text.split('\n')
    wrapped_lines = []
    
    for paragraph in paragraphs:
        if not paragraph.strip():
            wrapped_lines.append('')
            continue
            
        words = paragraph.split(' ')
        current_line = ''
        
        for word in words:
            # Test if adding this word would exceed max width
            test_line = current_line + (' ' if current_line else '') + word
            text_width = font.size(test_line)[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                # If current line is not empty, save it and start new line
                if current_line:
                    wrapped_lines.append(current_line)
                    current_line = word
                else:
                    # Single word is too long, break it
                    wrapped_lines.append(word)
        
        # Add remaining text
        if current_line:
            wrapped_lines.append(current_line)
    
    return wrapped_lines

def render_wrapped_text_lines(screen: pygame.Surface, lines: List[str], font: pygame.font.Font, 
                             color: tuple, start_x: int, start_y: int, line_spacing: int = 3) -> int:
    """
    Render a list of wrapped text lines
    
    Args:
        screen: Surface to render to
        lines: List of text lines to render
        font: Font to use
        color: Text color
        start_x: Starting X position
        start_y: Starting Y position
        line_spacing: Extra spacing between lines
        
    Returns:
        The Y position after the last line
    """
    current_y = start_y
    line_height = font.get_height()
    
    for line in lines:
        if line.strip():  # Only render non-empty lines
            text_surface = font.render(line, True, color)
            screen.blit(text_surface, (start_x, current_y))
        current_y += line_height + line_spacing
    
    return current_y

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

class EditableText:
    """An editable text input that supports clipboard operations with multi-line support"""
    
    def __init__(self, font: pygame.font.Font, rect: pygame.Rect, initial_text: str = "", ui_manager=None):
        self.font = font
        self.base_rect = rect.copy()  # Store original rect
        self.rect = rect
        self.text = initial_text
        self.cursor_pos = len(initial_text)
        self.selection_start = None
        self.selection_end = None
        self.focused = False
        self.ui_manager = ui_manager # Store reference to PasswordUI
        self.is_selecting = False  # Track if we're in the middle of a mouse selection
        
        # Multi-line and scrolling support
        self.line_height = font.get_height()
        self.padding = 5
        self.min_height = rect.height
        self.max_height = 150  # Maximum height before scrolling
        self.scroll_offset = 0
        self.wrapped_lines = []
        self.cursor_line = 0
        self.cursor_col = 0
        
        # Update wrapped lines
        self._update_wrapped_lines()
        
        # Undo/Redo functionality
        self.undo_stack = [(initial_text, len(initial_text))]  # Stack of (text, cursor_pos) tuples
        self.redo_stack = []  # Stack for redo operations
        self.max_undo_states = 50  # Limit undo history to prevent memory issues
        
    def _update_wrapped_lines(self):
        """Update wrapped lines and adjust height"""
        # Calculate max width for wrapping, accounting for scrollbar space
        scrollbar_space = 10 if len(self.text) > 100 else 0  # Estimate if scrollbar will be needed
        effective_max_width = self.base_rect.width - (self.padding * 2) - scrollbar_space
        
        if not self.text:
            self.wrapped_lines = [""]
        else:
            self.wrapped_lines = wrap_text(self.text, self.font, effective_max_width)
        
        # Calculate required height
        required_height = len(self.wrapped_lines) * self.line_height + (self.padding * 2)
        
        # Adjust height (between min and max)
        new_height = max(self.min_height, min(self.max_height, required_height))
        
        # Update rect height
        self.rect.height = new_height
        
        # Recalculate max width more accurately now that we know if scrollbar is needed
        visible_lines = (self.rect.height - self.padding * 2) // self.line_height
        scrollbar_needed = len(self.wrapped_lines) > visible_lines
        
        if scrollbar_needed:
            # Recalculate with scrollbar space
            effective_max_width = self.base_rect.width - (self.padding * 2) - 12  # 6px scrollbar + 6px margin
            self.wrapped_lines = wrap_text(self.text, self.font, effective_max_width)
        
        # Update cursor position in wrapped lines
        self._update_cursor_position()
        
        # Ensure cursor is visible (auto-scroll)
        self._ensure_cursor_visible()
    
    def _update_cursor_position(self):
        """Update cursor line and column based on cursor_pos"""
        if not self.wrapped_lines:
            self.cursor_line = 0
            self.cursor_col = 0
            return
        
        char_count = 0
        for line_idx, line in enumerate(self.wrapped_lines):
            if char_count + len(line) >= self.cursor_pos:
                self.cursor_line = line_idx
                self.cursor_col = self.cursor_pos - char_count
                return
            char_count += len(line)
            if line_idx < len(self.wrapped_lines) - 1:
                char_count += 1  # Account for spaces between wrapped parts
        
        # Cursor at end
        self.cursor_line = len(self.wrapped_lines) - 1
        self.cursor_col = len(self.wrapped_lines[-1]) if self.wrapped_lines else 0
    
    def _ensure_cursor_visible(self):
        """Ensure cursor is visible by adjusting scroll offset"""
        visible_lines = (self.rect.height - self.padding * 2) // self.line_height
        
        if self.cursor_line < self.scroll_offset:
            self.scroll_offset = self.cursor_line
        elif self.cursor_line >= self.scroll_offset + visible_lines:
            self.scroll_offset = self.cursor_line - visible_lines + 1
        
        # Ensure scroll offset is within bounds
        max_scroll = max(0, len(self.wrapped_lines) - visible_lines)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
    
    def _line_col_to_cursor_pos(self, line: int, col: int) -> int:
        """Convert line and column to absolute cursor position"""
        if not self.wrapped_lines:
            return 0
        
        pos = 0
        for i in range(min(line, len(self.wrapped_lines))):
            pos += len(self.wrapped_lines[i])
            if i < len(self.wrapped_lines) - 1:
                pos += 1  # Space between wrapped parts
        
        if line < len(self.wrapped_lines):
            pos += min(col, len(self.wrapped_lines[line]))
        
        return min(pos, len(self.text))
    
    def _pos_to_cursor(self, pos):
        """Convert mouse position to cursor position"""
        rel_x = pos[0] - self.rect.x - self.padding
        rel_y = pos[1] - self.rect.y - self.padding
        
        # Determine which line
        line_idx = self.scroll_offset + (rel_y // self.line_height)
        line_idx = max(0, min(line_idx, len(self.wrapped_lines) - 1))
        
        if line_idx >= len(self.wrapped_lines):
            return len(self.text)
        
        # Determine position within line
        line = self.wrapped_lines[line_idx]
        col = 0
        for i in range(len(line) + 1):
            char_width = self.font.size(line[:i])[0]
            if char_width > rel_x:
                col = i
                break
            col = i
        
        return self._line_col_to_cursor_pos(line_idx, col)
    
    def handle_event(self, event):
        """Handle input events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.focused = True
                self.cursor_pos = self._pos_to_cursor(event.pos)
                # Start selection
                self.selection_start = self.cursor_pos
                self.selection_end = self.cursor_pos
                self.is_selecting = True
                self._update_cursor_position()
                return True
            else:
                self.focused = False
                self.is_selecting = False
                return False
        
        if event.type == pygame.MOUSEBUTTONUP:
            if self.is_selecting:
                self.is_selecting = False
                # Clear selection if start and end are the same (just a click)
                if self.selection_start == self.selection_end:
                    self.selection_start = None
                    self.selection_end = None
                return True
        
        if event.type == pygame.MOUSEMOTION:
            if self.is_selecting and event.buttons[0]:  # Left mouse button held
                self.selection_end = self._pos_to_cursor(event.pos)
                self.cursor_pos = self.selection_end
                self._update_cursor_position()
                return True
        
        # Handle scroll wheel for long passwords
        if event.type == pygame.MOUSEWHEEL and self.focused:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_offset = max(0, min(
                    len(self.wrapped_lines) - 1,
                    self.scroll_offset - event.y
                ))
                return True
        
        if not self.focused:
            return False
        
        if event.type == pygame.KEYDOWN:
            # Handle Ctrl combinations
            if event.mod & pygame.KMOD_CTRL:
                if event.key == pygame.K_z:  # Undo
                    result = self._undo()
                    if result:
                        self._update_wrapped_lines()
                    return result
                elif event.key == pygame.K_y:  # Redo
                    result = self._redo()
                    if result:
                        self._update_wrapped_lines()
                    return result
                elif event.key == pygame.K_c:  # Copy
                    self._copy_selection()
                    return True
                elif event.key == pygame.K_v:  # Paste
                    self._save_state()  # Save state before paste
                    self._paste()
                    self._update_wrapped_lines()
                    return True
                elif event.key == pygame.K_x:  # Cut
                    self._save_state()  # Save state before cut
                    self._cut()
                    self._update_wrapped_lines()
                    return True
                elif event.key == pygame.K_a:  # Select all
                    self.selection_start = 0
                    self.selection_end = len(self.text)
                    self.cursor_pos = len(self.text)
                    self._update_cursor_position()
                    return True
            
            # Handle other keys
            if event.key == pygame.K_BACKSPACE:
                if self.selection_start is not None and self.selection_end is not None and self.selection_start != self.selection_end:
                    self._save_state()  # Save state before deletion
                    self._delete_selection()
                elif self.cursor_pos > 0:
                    self._save_state()  # Save state before deletion
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
                self._update_wrapped_lines()
                return True
            elif event.key == pygame.K_DELETE:
                if self.selection_start is not None and self.selection_end is not None and self.selection_start != self.selection_end:
                    self._save_state()  # Save state before deletion
                    self._delete_selection()
                elif self.cursor_pos < len(self.text):
                    self._save_state()  # Save state before deletion
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
                self._update_wrapped_lines()
                return True
            elif event.key == pygame.K_LEFT:
                if event.mod & pygame.KMOD_SHIFT:
                    # Shift+Left: extend selection
                    if self.selection_start is None:
                        self.selection_start = self.cursor_pos
                    if self.cursor_pos > 0:
                        self.cursor_pos -= 1
                    self.selection_end = self.cursor_pos
                else:
                    # Left: move cursor and clear selection
                    if self.cursor_pos > 0:
                        self.cursor_pos -= 1
                    self.selection_start = None
                    self.selection_end = None
                self._update_cursor_position()
                self._ensure_cursor_visible()
                return True
            elif event.key == pygame.K_RIGHT:
                if event.mod & pygame.KMOD_SHIFT:
                    # Shift+Right: extend selection
                    if self.selection_start is None:
                        self.selection_start = self.cursor_pos
                    if self.cursor_pos < len(self.text):
                        self.cursor_pos += 1
                    self.selection_end = self.cursor_pos
                else:
                    # Right: move cursor and clear selection
                    if self.cursor_pos < len(self.text):
                        self.cursor_pos += 1
                    self.selection_start = None
                    self.selection_end = None
                self._update_cursor_position()
                self._ensure_cursor_visible()
                return True
            elif event.key == pygame.K_UP:
                # Move cursor up one line
                if self.cursor_line > 0:
                    new_line = self.cursor_line - 1
                    new_col = min(self.cursor_col, len(self.wrapped_lines[new_line]))
                    self.cursor_pos = self._line_col_to_cursor_pos(new_line, new_col)
                    self._update_cursor_position()
                    self._ensure_cursor_visible()
                return True
            elif event.key == pygame.K_DOWN:
                # Move cursor down one line
                if self.cursor_line < len(self.wrapped_lines) - 1:
                    new_line = self.cursor_line + 1
                    new_col = min(self.cursor_col, len(self.wrapped_lines[new_line]))
                    self.cursor_pos = self._line_col_to_cursor_pos(new_line, new_col)
                    self._update_cursor_position()
                    self._ensure_cursor_visible()
                return True
            elif event.key == pygame.K_HOME:
                if event.mod & pygame.KMOD_SHIFT:
                    # Shift+Home: select to beginning
                    if self.selection_start is None:
                        self.selection_start = self.cursor_pos
                    self.cursor_pos = 0
                    self.selection_end = self.cursor_pos
                else:
                    # Home: move to beginning and clear selection
                    self.cursor_pos = 0
                    self.selection_start = None
                    self.selection_end = None
                self._update_cursor_position()
                self._ensure_cursor_visible()
                return True
            elif event.key == pygame.K_END:
                if event.mod & pygame.KMOD_SHIFT:
                    # Shift+End: select to end
                    if self.selection_start is None:
                        self.selection_start = self.cursor_pos
                    self.cursor_pos = len(self.text)
                    self.selection_end = self.cursor_pos
                else:
                    # End: move to end and clear selection
                    self.cursor_pos = len(self.text)
                    self.selection_start = None
                    self.selection_end = None
                self._update_cursor_position()
                self._ensure_cursor_visible()
                return True
            elif event.unicode and event.unicode.isprintable():
                self._save_state()  # Save state before typing
                if self.selection_start is not None and self.selection_end is not None and self.selection_start != self.selection_end:
                    self._delete_selection()
                self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                self.cursor_pos += 1
                self._update_wrapped_lines()
                return True
        
        return False
    
    def _save_state(self):
        """Save current state to undo stack"""
        current_state = (self.text, self.cursor_pos)
        # Only save if the state is different from the last one
        if not self.undo_stack or self.undo_stack[-1] != current_state:
            self.undo_stack.append(current_state)
            # Limit undo stack size
            if len(self.undo_stack) > self.max_undo_states:
                self.undo_stack.pop(0)
            # Clear redo stack when new action is performed
            self.redo_stack.clear()
    
    def _undo(self):
        """Undo the last action"""
        if len(self.undo_stack) > 1:  # Keep at least one state
            # Move current state to redo stack
            current_state = (self.text, self.cursor_pos)
            self.redo_stack.append(current_state)
            
            # Restore previous state
            self.undo_stack.pop()  # Remove current state
            previous_text, previous_cursor = self.undo_stack[-1]
            self.text = previous_text
            self.cursor_pos = previous_cursor
            
            # Clear selection
            self.selection_start = None
            self.selection_end = None
            
            return True
        return False
    
    def _redo(self):
        """Redo the last undone action"""
        if self.redo_stack:
            # Save current state to undo stack
            self.undo_stack.append((self.text, self.cursor_pos))
            
            # Restore next state
            next_text, next_cursor = self.redo_stack.pop()
            self.text = next_text
            self.cursor_pos = next_cursor
            
            # Clear selection
            self.selection_start = None
            self.selection_end = None
            
            return True
        return False
        
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
        """Render the multi-line text input with scrolling"""
        # Draw background
        bg_color = self.ui_manager.input_bg_color if self.ui_manager else (60, 60, 70)
        border_color = self.ui_manager.input_focused_border_color if self.focused and self.ui_manager else (self.ui_manager.input_border_color if self.ui_manager else (100,100,110))
        text_color = self.ui_manager.text_color if self.ui_manager else (255,255,255)
        selection_bg_color = self.ui_manager.selection_bg_color if self.ui_manager else (80, 100, 150)
        
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=3)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=3)
        
        # Calculate visible area
        visible_lines = (self.rect.height - self.padding * 2) // self.line_height
        start_line = self.scroll_offset
        end_line = min(len(self.wrapped_lines), start_line + visible_lines)
        
        # Draw text lines
        for line_idx in range(start_line, end_line):
            if line_idx >= len(self.wrapped_lines):
                break
                
            line = self.wrapped_lines[line_idx]
            y_pos = self.rect.y + self.padding + (line_idx - start_line) * self.line_height
            
            # Calculate line's absolute character range
            line_start_pos = self._line_col_to_cursor_pos(line_idx, 0)
            line_end_pos = self._line_col_to_cursor_pos(line_idx, len(line))
            
            # Draw selection background for this line
            if (self.selection_start is not None and self.selection_end is not None and
                self.selection_start != self.selection_end):
                
                sel_start = min(self.selection_start, self.selection_end)
                sel_end = max(self.selection_start, self.selection_end)
                
                # Check if selection overlaps with this line
                if sel_start < line_end_pos and sel_end > line_start_pos:
                    # Calculate selection bounds within this line
                    line_sel_start = max(0, sel_start - line_start_pos)
                    line_sel_end = min(len(line), sel_end - line_start_pos)
                    
                    if line_sel_start < line_sel_end:
                        # Calculate pixel positions for selection
                        start_x_offset = self.font.size(line[:line_sel_start])[0] if line_sel_start > 0 else 0
                        end_x_offset = self.font.size(line[:line_sel_end])[0]
                        
                        sel_rect = pygame.Rect(
                            self.rect.x + self.padding + start_x_offset,
                            y_pos,
                            end_x_offset - start_x_offset,
                            self.line_height
                        )
                        pygame.draw.rect(screen, selection_bg_color, sel_rect)
            
            # Draw the text line
            if line:
                text_surface = self.font.render(line, True, text_color)
                screen.blit(text_surface, (self.rect.x + self.padding, y_pos))
        
        # Draw cursor
        if self.focused and pygame.time.get_ticks() % 1000 < 500:
            if (start_line <= self.cursor_line < end_line):
                cursor_line = self.wrapped_lines[self.cursor_line] if self.cursor_line < len(self.wrapped_lines) else ""
                cursor_x_offset = self.font.size(cursor_line[:self.cursor_col])[0]
                cursor_x = self.rect.x + self.padding + cursor_x_offset
                cursor_y = self.rect.y + self.padding + (self.cursor_line - start_line) * self.line_height
                
                pygame.draw.line(screen, text_color, 
                               (cursor_x, cursor_y), 
                               (cursor_x, cursor_y + self.line_height), 2)
        
        # Draw scrollbar if needed
        if len(self.wrapped_lines) > visible_lines:
            self._draw_scrollbar(screen, visible_lines)
    
    def _draw_scrollbar(self, screen, visible_lines):
        """Draw scrollbar for multi-line text"""
        scrollbar_width = 6
        scrollbar_margin = 3  # Increased margin to keep scrollbar more inside
        scrollbar_x = self.rect.right - scrollbar_width - scrollbar_margin
        scrollbar_y = self.rect.y + self.padding
        scrollbar_height = self.rect.height - self.padding * 2
        
        # Ensure scrollbar is within input field bounds
        if scrollbar_x + scrollbar_width > self.rect.right - 1:
            scrollbar_x = self.rect.right - scrollbar_width - 1
        
        # Scrollbar background
        bg_color = self.ui_manager.scrollbar_bg_color if self.ui_manager else (80, 80, 90)
        scrollbar_bg = pygame.Rect(scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height)
        pygame.draw.rect(screen, bg_color, scrollbar_bg, border_radius=3)
        
        # Scrollbar thumb
        if len(self.wrapped_lines) > visible_lines:
            thumb_height = max(20, int(scrollbar_height * visible_lines / len(self.wrapped_lines)))
            max_scroll = len(self.wrapped_lines) - visible_lines
            thumb_y = scrollbar_y + int((scrollbar_height - thumb_height) * self.scroll_offset / max_scroll) if max_scroll > 0 else scrollbar_y
            
            # Clamp thumb_y and thumb_height to stay within scrollbar_bg
            thumb_y = max(scrollbar_y, min(thumb_y, scrollbar_y + scrollbar_height - thumb_height))
            if thumb_y + thumb_height > scrollbar_y + scrollbar_height:
                thumb_height = scrollbar_y + scrollbar_height - thumb_y # Adjust height to fit
            
            thumb_color = self.ui_manager.scrollbar_thumb_color if self.ui_manager else (120, 120, 130)
            thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
            pygame.draw.rect(screen, thumb_color, thumb_rect, border_radius=3)

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
            print("Successfully loaded custom font: Unifontexmono-2vrqo.ttf")
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
        self.close_callback = None  # Callback for when UI is closed via X button
        self.collected_rules = []
        
        # UI dimensions
        self.width = 700
        self.height = 600  # Increased from 500 to 600
        self.x = (screen.get_width() - self.width) // 2
        self.y = (screen.get_height() - self.height) // 2
        
        # Close button (X) dimensions
        self.close_button_size = 30
        self.close_button_x = self.x + self.width - self.close_button_size - 10
        self.close_button_y = self.y + 10
        self.close_button_rect = pygame.Rect(self.close_button_x, self.close_button_y, self.close_button_size, self.close_button_size)
        self.close_button_hovered = False
        
        # Text widgets
        self.rules_text = None
        self.password_input = None
        
    def show(self, rules: List[str], door, callback: Callable = None, collected_rules: List[str] = None, preserved_password: str = "", close_callback: Callable = None):
        """Show the password UI with given rules"""
        self.visible = True
        self.rules = rules
        self.door = door
        self.callback = callback
        self.close_callback = close_callback  # New callback for when UI is closed
        self.collected_rules = collected_rules or []
        self.validation_results = {}
        self.message = "Enter a password that follows all the rules:"
        
        # Create rules text showing total required rules with collected/uncollected status
        rules_content = "Password Requirements:\n\n"
        
        # Get the total number of rules required (from door's required_rules)
        total_required = door.required_rules if door else len(rules)
        
        # Calculate max width for text wrapping (password UI width minus padding)
        max_text_width = self.width - 80  # 40 padding on each side + some extra margin
        
        # Track which lines belong to which rules for proper validation coloring
        self.rule_line_mapping = {}  # Maps line index to rule index
        current_line_index = 2  # Start after "Password Requirements:" and empty line
        
        # Show all rule slots (collected + uncollected) with text wrapping
        for i in range(total_required):
            if i < len(self.collected_rules):
                # Show the actual collected rule with wrapping
                rule_text = f"{i+1}. {self.collected_rules[i]}"
                wrapped_lines = wrap_text(rule_text, self.small_font, max_text_width)
                
                # Mark all lines of this rule with the rule index
                for line_offset in range(len(wrapped_lines)):
                    self.rule_line_mapping[current_line_index + line_offset] = i
                
                rules_content += '\n'.join(wrapped_lines) + "\n\n"
                current_line_index += len(wrapped_lines) + 1  # +1 for empty line
            else:
                # Show placeholder for uncollected rule
                rules_content += f"{i+1}. ????\n\n"
                self.rule_line_mapping[current_line_index] = i  # Mark placeholder line
                current_line_index += 2  # +2 for rule line and empty line
        
        rules_rect_y_position = self.y + 80 # Assuming 80px for title and message area
        new_rules_rect_height = 250 # Reduced from 280px
        rules_rect = pygame.Rect(self.x + 20, rules_rect_y_position, self.width - 40, new_rules_rect_height)
        
        # Update existing rules text or create new one
        if self.rules_text:
            self.rules_text.update_content(rules_content)
            self.rules_text.rect = rules_rect # Ensure rect is updated
            self.rules_text.set_ui_manager(self) # Ensure ui_manager is set
        else:
            self.rules_text = SelectableText(rules_content, self.small_font, self.text_color, rules_rect, self.selection_bg_color)
            self.rules_text.set_ui_manager(self) # Set ui_manager
        self.rules_text.max_visible_lines = max(1, self.rules_text.rect.height // self.rules_text.line_height)
        self.rules_text.max_scroll = max(0, len(self.rules_text.lines) - self.rules_text.max_visible_lines)
        if self.rules_text.max_scroll > 0 and len(self.rules_text.lines) > self.rules_text.max_visible_lines:
             self.rules_text.scroll_to_bottom()

        # Create password input with preserved password - position it properly within dialog bounds
        # The Y position of input_rect will be determined by the elements above it in the render() method.
        # For initialization, just provide a placeholder Y, its actual Y is set in render().
        # However, the render method now calculates it based on the rules_rect_height from render's local var.
        # So, let's ensure the initial placement in `show` is also consistent with `render` logic.
        
        # Approximate y for input_rect based on new_rules_rect_height for consistency, though render() recalculates.
        approx_input_label_y = rules_rect_y_position + new_rules_rect_height + 15 # 15 is input_field_y_offset
        approx_input_field_y = approx_input_label_y + self.font.get_height() + 10 # 10 is input_label_to_field_offset
        input_rect = pygame.Rect(self.x + 20, approx_input_field_y, self.width - 40, 35) # 35 is min_height
        self.password_input = EditableText(self.font, input_rect, preserved_password, self)
        
        # Auto-focus the password input so user can start typing immediately
        self.password_input.focused = True
        
        # Update validation immediately if we have a preserved password
        if preserved_password:
            self._update_validation()
        
    def hide(self):
        """Hide the password UI"""
        # Call close callback with current password if available
        if self.close_callback and self.password_input:
            self.close_callback(self.password_input.text)
        
        self.visible = False
        self.rules_text = None
        self.password_input = None
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events"""
        if not self.visible:
            return False
        
        # Handle mouse hover for close button
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.close_button_hovered = self.close_button_rect.collidepoint(mouse_pos)
        
        # Handle mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            # Check if close button was clicked
            if self.close_button_rect.collidepoint(mouse_pos):
                self.hide()
                return True
            
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
                # Only handle if not clicking close button
                if not self.close_button_rect.collidepoint(event.pos):
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
            # Pass the combined rules count (accumulated + current) to the door validation
            combined_rules_count = len(self.collected_rules) if self.collected_rules else 0
            result = self.door.try_password(self.password_input.text, combined_rules_count)
            self.callback(result)
            
            if result.get("success", False):
                self.hide()
            else:
                self.message = result.get("message", "Incorrect password")
    
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
        rules_rect_height = 250 # Consistent with show() method: Reduced from 280 to 250
        input_field_y_offset = 15  # Reduced from 30 to 15 to move input field higher
        input_label_to_field_offset = 10 # Space between input label and field
        validation_text_y_offset = 10 # Space between input field and validation
        
        # Draw main UI panel
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(self.screen, self.panel_bg_color, panel_rect, border_radius=10) # Added rounded corners
        pygame.draw.rect(self.screen, self.panel_border_color, panel_rect, 2, border_radius=10)
        
        # Draw close button (X)
        close_button_color = (200, 100, 100) if self.close_button_hovered else (150, 150, 160)
        close_button_bg_color = (70, 70, 80) if self.close_button_hovered else (60, 60, 70)
        
        # Draw close button background
        pygame.draw.rect(self.screen, close_button_bg_color, self.close_button_rect, border_radius=3)
        pygame.draw.rect(self.screen, close_button_color, self.close_button_rect, 2, border_radius=3)
        
        # Draw X symbol
        center_x = self.close_button_rect.centerx
        center_y = self.close_button_rect.centery
        offset = 8
        
        # Draw the X lines
        pygame.draw.line(self.screen, close_button_color, 
                        (center_x - offset, center_y - offset), 
                        (center_x + offset, center_y + offset), 3)
        pygame.draw.line(self.screen, close_button_color, 
                        (center_x + offset, center_y - offset), 
                        (center_x - offset, center_y + offset), 3)
        
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
            
            # Create line colors based on rule validation and line mapping
            line_colors = []
            for line_index, line in enumerate(self.rules_text.lines):
                if line_index in self.rule_line_mapping:
                    # This line belongs to a specific rule
                    rule_index = self.rule_line_mapping[line_index]
                    
                    if line.strip().endswith("????"):
                        # Uncollected rule placeholder
                        line_colors.append(self.hidden_rule_color)
                    else:
                        # Check validation for this specific rule
                        rule_satisfied = False
                        if self.validation_results and rule_index < len(self.collected_rules):
                            # Get the actual rule text and check validation
                            actual_rule = self.collected_rules[rule_index]
                            for rule, satisfied in self.validation_results.items():
                                if rule == actual_rule:
                                    rule_satisfied = satisfied
                                    break
                        
                        # Apply appropriate color
                        if rule_satisfied:
                            line_colors.append(self.satisfied_rule_color)
                        else:
                            line_colors.append(self.unsatisfied_rule_color)
                else:
                    # Header text or empty lines use default color
                    line_colors.append(self.text_color)
            
            self.rules_text.set_line_colors(line_colors)
            self.rules_text.render(self.screen)
        
        # --- Input Label and Field --- 
        current_y = rules_rect_y + rules_rect_height + input_field_y_offset

        input_label = self.font.render("Enter Password:", True, self.text_color)
        self.screen.blit(input_label, (self.x + panel_padding, current_y))
        current_y += input_label.get_height() + input_label_to_field_offset
        
        if self.password_input:
            self.password_input.rect.y = current_y
            self.password_input.rect.x = self.x + panel_padding
            self.password_input.rect.width = self.width - panel_padding*2
            # The EditableText.render() method handles its own height adjustment.
            self.password_input.render(self.screen)
            current_y += self.password_input.rect.height # Use actual height of input box
        else:
            current_y += 35 # Default height if no input box
        
        # --- Validation Text --- 
        validation_text_y = current_y + validation_text_y_offset
        if self.password_input:
            valid_count = sum(1 for result in self.validation_results.values() if result) if self.validation_results else 0
            total_collected = len(self.collected_rules)
            total_required = self.door.required_rules if self.door else total_collected
            
            # Character count
            char_count = len(self.password_input.text)
            char_count_text = f"Characters: {char_count}"
            
            validation_text = f"Rules satisfied: {valid_count}/{total_collected} | Total required: {total_collected}/{total_required} | {char_count_text}"
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
            print("Successfully loaded custom font for MessageUI: Unifontexmono-2vrqo.ttf")
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
            print("Successfully loaded custom font for RulesDisplayUI: Unifontexmono-2vrqo.ttf")
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load custom font for RulesDisplayUI: {e}")
            # Fallback to default font if custom font fails to load
            self.font = pygame.font.Font(None, 18)
            self.title_font = pygame.font.Font(None, 20)
        
        # Minimize/maximize state
        self.is_minimized = False
        self.minimize_button_size = 20
        self.minimize_button_hovered = False
        self.minimize_button_rect = None  # Will be set during render
        
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
        
    def render(self, rules: List[str]):
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
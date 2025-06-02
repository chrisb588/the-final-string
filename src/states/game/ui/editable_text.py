# UI Component for Textfield on Password Judge interface

import pygame
from ..utils.wrap_text import wrap_text
import pyperclip

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

    def update(self, delta_time: float):
        """Update editable text state"""
        if not self.focused:
            return

        # Update cursor blink timing
        current_time = pygame.time.get_ticks()
        self.cursor_visible = (current_time % 1000 < 500)
        
    def _update_wrapped_lines(self):
        """Update wrapped lines and adjust height"""
        # Calculate max width for wrapping
        scrollbar_width = 12
        total_padding = self.padding * 2
        effective_width = self.rect.width - total_padding - scrollbar_width

        # Wrap text
        if not self.text:
            self.wrapped_lines = [""]
        else:
            # Split text into words and wrap
            words = self.text.split()
            current_line = []
            current_width = 0
            self.wrapped_lines = []

            for word in words:
                word_surface = self.font.render(word + " ", True, (0, 0, 0))
                word_width = word_surface.get_width()

                if current_width + word_width > effective_width:
                    # Start new line
                    if current_line:
                        self.wrapped_lines.append(" ".join(current_line))
                    current_line = [word]
                    current_width = word_width
                else:
                    current_line.append(word)
                    current_width += word_width

            if current_line:
                self.wrapped_lines.append(" ".join(current_line))

            if not self.wrapped_lines:
                self.wrapped_lines = [""]

        # Calculate required height
        line_count = len(self.wrapped_lines)
        min_lines = 1
        max_lines = 5  # Maximum visible lines
        visible_lines = max(min_lines, min(max_lines, line_count))
        
        # Calculate new height
        new_height = (visible_lines * self.line_height) + (self.padding * 2)
        self.rect.height = max(self.min_height, min(self.max_height, new_height))

        # Update cursor position
        self._update_cursor_position()
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
        
        if event.type in (pygame.KEYDOWN, pygame.KEYUP):
            # Handle key repeat for navigation keys
            keys = pygame.key.get_pressed()
            
            # Handle continuous cursor movement
            if event.type == pygame.KEYDOWN or (event.type == pygame.KEYUP and any([
                keys[pygame.K_LEFT], keys[pygame.K_RIGHT], 
                keys[pygame.K_UP], keys[pygame.K_DOWN]])):
                
                if keys[pygame.K_LEFT]:
                    if event.mod & pygame.KMOD_SHIFT:
                        if self.selection_start is None:
                            self.selection_start = self.cursor_pos
                        if self.cursor_pos > 0:
                            self.cursor_pos -= 1
                        self.selection_end = self.cursor_pos
                    else:
                        if self.cursor_pos > 0:
                            self.cursor_pos -= 1
                        self.selection_start = None
                        self.selection_end = None
                    self._update_cursor_position()
                    self._ensure_cursor_visible()
                    return True
                    
                elif keys[pygame.K_RIGHT]:
                    if event.mod & pygame.KMOD_SHIFT:
                        if self.selection_start is None:
                            self.selection_start = self.cursor_pos
                        if self.cursor_pos < len(self.text):
                            self.cursor_pos += 1
                        self.selection_end = self.cursor_pos
                    else:
                        if self.cursor_pos < len(self.text):
                            self.cursor_pos += 1
                        self.selection_start = None
                        self.selection_end = None
                    self._update_cursor_position()
                    self._ensure_cursor_visible()
                    return True

        if event.type == pygame.KEYDOWN:
            # Handle key repeat for navigation keys
            keys = pygame.key.get_pressed()
            
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
                if self.selection_start is not None and self.selection_end is not None:
                    self._delete_selection()
                self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                self.cursor_pos += 1
                self._update_wrapped_lines()  # Update wrapping after text changes
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
        """Render the editable text with wrapping"""
        # Draw background and border
        bg_color = self.ui_manager.input_bg_color if self.ui_manager else (60, 60, 70)
        border_color = (
            self.ui_manager.input_focused_border_color if self.focused and self.ui_manager 
            else self.ui_manager.input_border_color if self.ui_manager 
            else (100, 100, 110)
        )
        text_color = self.ui_manager.text_color if self.ui_manager else (255, 255, 255)
        
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=3)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=3)
        
        # Calculate visible area
        visible_lines = (self.rect.height - self.padding * 2) // self.line_height
        start_line = self.scroll_offset
        end_line = min(len(self.wrapped_lines), start_line + visible_lines)
        
        # Draw text lines
        for line_idx in range(start_line, end_line):
            line = self.wrapped_lines[line_idx]
            y_pos = self.rect.y + self.padding + (line_idx - start_line) * self.line_height
            
            if line:
                text_surface = self.font.render(line, True, text_color)
                screen.blit(text_surface, (self.rect.x + self.padding, y_pos))

        # Draw cursor if focused
        if self.focused and self.cursor_visible:
            if start_line <= self.cursor_line < end_line:
                cursor_line = self.wrapped_lines[self.cursor_line]
                cursor_x = self.rect.x + self.padding + self.font.size(cursor_line[:self.cursor_col])[0]
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
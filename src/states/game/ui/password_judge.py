import pygame
from typing import List, Dict, Optional, Callable
import os
from ..utils.wrap_text import wrap_text
from .selectable_text import SelectableText
from .editable_text import EditableText

class PasswordUI:
    """UI for displaying password rules and handling password input with text selection"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        
        # Load custom font from assets/fonts directory
        self._init_font()
        
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

        self.validate_button_rect = None
        self.validate_button_hovered = False
        self.validate_button_color = (80, 130, 180)  # Default blue
        self.validate_button_hover_color = (100, 150, 200)  # Lighter blue when hovered
        self.validate_button_text_color = (220, 220, 230)  # Light gray text

        # Initialize dimensions
        self._init_dimensions()

    def _init_font(self):
        """Initialize font with fallback"""
        try:
            # Get the current file's directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Navigate to the main directory (4 levels up from current file)
            main_dir = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
            
            # Construct path to font in assets directory
            content_font_path = os.path.join(main_dir, 'assets', 'fonts', 'UnifontEX.ttf')
            label_font_path = os.path.join(main_dir, 'assets', 'fonts', 'PixelSerif.ttf')
            
            # Load font with error handling
            if os.path.exists(content_font_path) and os.path.exists(label_font_path):
                self.font = pygame.font.Font(content_font_path, 20)  
                self.label_font = pygame.font.Font(label_font_path, 26)
                self.title_font = pygame.font.Font(label_font_path, 42) 
                self.small_font = pygame.font.Font(content_font_path, 16) 
                print("Successfully loaded custom fonts")
            else:
                print(f"Warning: Font file not found at {content_font_path} and {label_font_path}")
                self.font = pygame.font.Font(None, 32)
        except (pygame.error, IOError) as e:
            print(f"Warning: Could not initialize PauseButton font: {e}")
            self.font = pygame.font.SysFont('arial', 32)
        
    def show(self, rules: List[str], door, callback: Callable = None, collected_rules: List[str] = None, preserved_password: str = "", close_callback: Callable = None):
        """Show the password UI with given rules"""
        self.visible = True
        self.rules = rules
        self.door = door
        self.callback = callback
        self.close_callback = close_callback  # New callback for when UI is closed
        self.collected_rules = collected_rules or []
        self.validation_results = {}
        self.message = "Your Password Must Adhere to the Ruleset"
        
        # Create rules text showing total required rules with collected/uncollected status
        rules_content = ""
        
        # Get the total number of rules required (from door's required_rules)
        total_required = door.required_rules if door else len(rules)
        
        # Calculate max width for text wrapping (password UI width minus padding)
        max_text_width = self.width - 80  # 40 padding on each side + some extra margin
        
        # Track which lines belong to which rules for proper validation coloring
        self.rule_line_mapping = {}  # Maps line index to rule index
        current_line_index = 0  # Start after "Password Requirements:" and empty line
        
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
        
        rules_rect_y_position = self.y + 120 # Assuming 80px for title and message area
        new_rules_rect_height = 250 # Reduced from 280px
        rules_rect = pygame.Rect(self.x + 20, rules_rect_y_position, self.width - 40, new_rules_rect_height)

        # Update existing rules text or create new one
        if self.rules_text:
            self.rules_text.update_content(rules_content)
            self.rules_text.rect = rules_rect
        else:
            self.rules_text = SelectableText(
                rules_content, 
                self.small_font, 
                self.text_color, 
                rules_rect, 
                self.selection_bg_color,
                interactive=True  # Make rules text non-interactive
            )

        self.rules_text.set_ui_manager(self)
        self.rules_text.max_visible_lines = max(1, self.rules_text.rect.height // self.rules_text.line_height)
        self.rules_text.max_scroll = max(0, len(self.rules_text.lines) - self.rules_text.max_visible_lines)
        
        # Only scroll to bottom if we have collected rules, otherwise stay at top
        if (self.rules_text.max_scroll > 0 and len(self.rules_text.lines) > self.rules_text.max_visible_lines 
            and len(self.collected_rules) > 0):
             self.rules_text.scroll_to_bottom()
        else:
            # Stay at top when no rules are collected yet
            self.rules_text.scroll_to_top()

        # Create password input with preserved password - position it properly within dialog bounds
        # The Y position of input_rect will be determined by the elements above it in the render() method.
        # For initialization, just provide a placeholder Y, its actual Y is set in render().
        # However, the render method now calculates it based on the rules_rect_height from render's local var.
        # So, let's ensure the initial placement in `show` is also consistent with `render` logic.
        
        # Approximate y for input_rect based on new_rules_rect_height for consistency, though render() recalculates.
        approx_input_label_y = rules_rect_y_position + new_rules_rect_height + 4 # 8 is input_field_y_offset
        approx_input_field_y = approx_input_label_y + self.font.get_height() + 10 # 10 is input_label_to_field_offset
        input_rect = pygame.Rect(self.x + 20, approx_input_field_y, self.width - 40, 35) # 35 is min_height
        self.password_input = EditableText(self.font, input_rect, preserved_password, self)
        
        # Auto-focus the password input so user can start typing immediately
        self.password_input.focused = True
        
        # Update validation immediately if we have a preserved password
        if preserved_password:
            self._update_validation()
        else:
            # Even without a preserved password, scroll to first invalid rule on initial display
            self._scroll_to_first_invalid_rule()
        
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
            if self.validate_button_rect:
                self.validate_button_hovered = self.validate_button_rect.collidepoint(event.pos)
        
        # Handle mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            # Check if close button was clicked
            if self.close_button_rect.collidepoint(mouse_pos):
                self.hide()
                return True
            if event.button == 1 and self.validate_button_rect:  # Left click
                if self.validate_button_rect.collidepoint(event.pos):
                    self._validate_password()
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
            
            self.callback(result)  # Call callback after handling

            # Remove message display and directly handle result
            if result.get("success", False):
                self.hide()  # Close the password UI immediately on success
    
    def _update_validation(self):
        """Update real-time validation results"""
        if self.door and self.password_input:
            import sys
            import os
            # Add the src directory to the path so we can import game_state
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from rules import game_state
            # Validate against collected rules only
            self.validation_results = game_state.validate_password_against_all_rules(self.password_input.text, self.collected_rules)
            
            # Scroll to first invalid rule after validation update
            self._scroll_to_first_invalid_rule()
    
    def _scroll_to_first_invalid_rule(self):
        """Scroll the rules text to show the first rule that isn't satisfied yet"""
        if not self.rules_text or not self.collected_rules or not hasattr(self, 'rule_line_mapping'):
            return
        
        # Find the first unsatisfied rule
        first_invalid_rule_index = None
        for i, rule in enumerate(self.collected_rules):
            if not self.validation_results.get(rule, False):
                first_invalid_rule_index = i
                break
        
        # If all rules are satisfied, don't scroll
        if first_invalid_rule_index is None:
            return
        
        # Find the line number corresponding to this rule
        target_line = None
        for line_idx, rule_idx in self.rule_line_mapping.items():
            if rule_idx == first_invalid_rule_index:
                target_line = line_idx
                break
        
        # Scroll to the target line if found
        if target_line is not None:
            self.rules_text.scroll_to_line(target_line)

    def update(self, delta_time: float):
        """Update UI elements"""
        try:
            if self.visible and self.rules_text:
                self.rules_text.update(delta_time)
            
            # Update password input if it exists
            if self.visible and self.password_input:
                self.password_input.update(delta_time)
                
        except Exception as e:
            print(f"Error updating PasswordUI: {e}")

    def _init_dimensions(self):
        """Initialize/update UI dimensions based on screen size"""
        # Base dimensions
        self.width = min(700, self.screen.get_width() - 40)  # Max width of 700 or screen width - 40
        self.height = min(600, self.screen.get_height() - 40)  # Max height of 600 or screen height - 40
        
        # Center the UI on screen
        self.x = (self.screen.get_width() - self.width) // 2
        self.y = (self.screen.get_height() - self.height) // 2
        
        # Update close button position
        self.close_button_size = 30
        self.close_button_x = self.x + self.width - self.close_button_size - 10
        self.close_button_y = self.y + 10
        self.close_button_rect = pygame.Rect(
            self.close_button_x, 
            self.close_button_y, 
            self.close_button_size, 
            self.close_button_size
        )
        
        # Update rules text area if it exists
        if self.rules_text:
            rules_rect_y = self.y + 120  # Position after title and message
            rules_rect = pygame.Rect(
                self.x + 20, 
                rules_rect_y, 
                self.width - 40, 
                250  # Fixed height for rules area
            )
            self.rules_text.rect = rules_rect
        
        # Update password input area if it exists
        if self.password_input:
            input_rect = pygame.Rect(
                self.x + 20,
                self.y + 400,  # Position after rules area
                self.width - 40,
                35  # Fixed height for input
            )
            self.password_input.rect = input_rect

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
        input_field_y_offset = 4  # Reduced from 15 to 8 to move input field higher and give more room for validate button
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
        title_text = self.title_font.render("The Password Judge", True, self.title_text_color)
        title_x = self.x + (self.width - title_text.get_width()) // 2
        self.screen.blit(title_text, (title_x, self.y + panel_padding))

        # Draw message
        message_text_y = self.y + panel_padding + title_text.get_height() + 5
        message_text = self.small_font.render(self.message, True, self.message_color)
        message_x = self.x + (self.width - message_text.get_width()) // 2
        self.screen.blit(message_text, (message_x, message_text_y))

        # Draw rules title
        rules_title = self.label_font.render("The Ruleset", True, self.text_color)
        rules_title_x = self.x + (self.width - rules_title.get_width()) // 2
        rules_title_y = message_text_y + message_text.get_height() + 20  # Small gap after message
        self.screen.blit(rules_title, (rules_title_x, rules_title_y))

        # Draw rules rectangle
        rules_rect_y = rules_title_y + rules_title.get_height() + 5  # Small gap after rules title
        rules_rect = pygame.Rect(self.x + panel_padding, rules_rect_y, self.width - panel_padding*2, rules_rect_height)

        # Inside the render method where line colors are set
        if self.rules_text:
            self.rules_text.rect = rules_rect # Update rect in case it changed
            
            # Create line colors based on rule validation and line mapping
            line_colors = []
            for line_index, line in enumerate(self.rules_text.lines):
                if line_index in self.rule_line_mapping:
                    rule_index = self.rule_line_mapping[line_index]
                    if rule_index < len(self.collected_rules):
                        # Get validation result for this rule
                        rule = self.collected_rules[rule_index]
                        is_valid = self.validation_results.get(rule, False)
                        line_colors.append(self.satisfied_rule_color if is_valid else self.unsatisfied_rule_color)
                    else:
                        # Hidden/uncollected rule
                        line_colors.append(self.hidden_rule_color)
                else:
                    # Non-rule lines (empty lines, headers, etc.)
                    line_colors.append(self.text_color)
            
            self.rules_text.set_line_colors(line_colors)
            self.rules_text.render(self.screen)
        
        # --- Input Label and Field --- 
        current_y = rules_rect_y + rules_rect_height + input_field_y_offset

        input_label = self.font.render("Type your password on the validator field:", True, self.text_color)
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

        validation_text_height = self.small_font.get_height()
        button_y = validation_text_y + validation_text_height + 15  # Space after validation text
        
        # Create button rectangle
        button_width = 120
        button_height = 35
        button_x = self.x + (self.width - button_width) // 2  # Center horizontally
        self.validate_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Draw button with hover effect
        button_color = self.validate_button_hover_color if self.validate_button_hovered else self.validate_button_color
        pygame.draw.rect(self.screen, button_color, self.validate_button_rect, border_radius=5)
        pygame.draw.rect(self.screen, (100, 100, 110), self.validate_button_rect, 2, border_radius=5)  # Border
        
        # Draw button text
        button_text = self.font.render("Validate", True, self.validate_button_text_color)
        text_x = button_x + (button_width - button_text.get_width()) // 2
        text_y = button_y + (button_height - button_text.get_height()) // 2
        self.screen.blit(button_text, (text_x, text_y))

    def _validate_password(self):
        """Validate password and handle result"""
        if not self.password_input or not self.password_input.text:
            self.message = "Please enter a password first!"
            return
            
        # Try password on door
        if self.door and self.callback:
            result = self.door.try_password(self.password_input.text)
            self.callback(result)
            
            if not result.get("success", False):
                self.message = "Password doesn't satisfy the ruleset!"
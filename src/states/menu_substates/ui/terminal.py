from dotenv import load_dotenv
import os
import sys

# Load environment variables first
load_dotenv()

# Add the path to sys.path so Python can find modules
pythonpath = os.environ.get('PYTHONPATH')
if pythonpath and pythonpath not in sys.path:
    sys.path.insert(0, pythonpath)

from constants import *
import pygame

class Terminal:
    def __init__(self, font):
        self.font = font
        self.lines = []
        self.dot_count = 0
        self.last_update = 0
        self.update_interval = 300  # ms between dot animations
        self.line_height = font.get_height() + 5  # Height of each line including spacing
        self.target_y_positions = []  # Target Y positions for each line
        self.current_y_positions = []  # Current Y positions for smooth animation
        self.animation_speed = 0.2  # Adjust this to control animation speed (0-1)
        self.default_color = TERMINAL_GREEN
        
    def add_line(self, text, animate_dots=False, color=TERMINAL_GREEN, font=None, center=False):
        """Add a new line to the terminal with position tracking, color, custom font, and centering"""
        # Shift existing lines' target positions up
        for i in range(len(self.target_y_positions)):
            self.target_y_positions[i] = i * self.line_height
            
        # Add new line at the bottom
        self.lines.append({
            "text": text,
            "animate_dots": animate_dots,
            "color": color,
            "font": font if font else self.font, # Use custom font or default
            "center": center # Store centering preference
        })
        
        bottom_position = len(self.lines) * self.line_height
        self.target_y_positions.append(bottom_position)
        self.current_y_positions.append(bottom_position)
    
    def update(self):
        """Update dot animation"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.update_interval:
            self.dot_count = (self.dot_count + 1) % 4
            self.last_update = current_time
            
        # Animate line positions
        for i in range(len(self.current_y_positions)):
            target = self.target_y_positions[i]
            current = self.current_y_positions[i]
            if current != target:
                self.current_y_positions[i] += (target - current) * self.animation_speed
    
    def render(self, surface, base_pos):
        """Render all lines with newest at bottom"""
        for i, line in enumerate(self.lines):
            text = line["text"]
            if line["animate_dots"]:
                text += "." * self.dot_count
            
            current_font = line.get("font", self.font) # Get the font for this line
            center_line = line.get("center", False) # Check if this line should be centered

            # Handle colored text segments
            if isinstance(line.get("color"), dict):
                default_color = line.get("default_color", self.default_color)
                
                # Calculate total width for centering if needed
                total_width = 0
                if center_line:
                    temp_x = 0
                    for segment_text, _ in line["color"].items():
                        # Account for text before and after specific colored segments
                        # This part might need refinement if default_color text is substantial
                        # For now, assumes colored segments dominate for centering calculations
                        # A more robust way would pre-calculate width of the entire formatted line
                        s_surface = current_font.render(segment_text, True, default_color) # Use default for width calc
                        total_width += s_surface.get_width()
                    # A simpler way if we assume the `text` field is the full string:
                    if not line["color"].items(): # handles case where line might be all default color
                         total_width = current_font.render(text, True, default_color).get_width()
                    else: # if there are colored segments, sum their widths
                        # this is a simplification. For perfect centering of mixed color lines,
                        # render the whole line to a temp surface first to get its true width.
                        # For now, we'll sum widths of explicitly colored parts if they exist
                        # or use the full text if no specific color dict is provided (implies all default color)
                        pass # total_width is already calculated based on colored segments

                x_pos_start = base_pos[0]
                if center_line:
                    x_pos_start = (surface.get_width() - total_width) // 2

                x_pos = x_pos_start
                y_pos = base_pos[1] - ((len(self.lines) - 1 - i) * self.line_height)

                # Split text and render each segment
                current_pos_in_text = 0
                rendered_segments = False
                for segment_text, segment_color in line["color"].items():
                    start_idx = text.find(segment_text, current_pos_in_text)
                    if start_idx != -1:
                        # Render text before this segment with default_color
                        if start_idx > current_pos_in_text:
                            before_text = text[current_pos_in_text:start_idx]
                            before_surface = current_font.render(before_text, True, default_color)
                            surface.blit(before_surface, (x_pos, y_pos))
                            x_pos += before_surface.get_width()
                        
                        # Render colored segment
                        segment_surface = current_font.render(segment_text, True, segment_color)
                        surface.blit(segment_surface, (x_pos, y_pos))
                        x_pos += segment_surface.get_width()
                        current_pos_in_text = start_idx + len(segment_text)
                        rendered_segments = True
                
                # Render any remaining text (or full text if no segments matched) with default_color
                if current_pos_in_text < len(text):
                    remaining_text = text[current_pos_in_text:]
                    remaining_surface = current_font.render(remaining_text, True, default_color)
                    # If centering and no specific segments were rendered, this is the main text to center
                    if center_line and not rendered_segments:
                        x_pos = (surface.get_width() - remaining_surface.get_width()) // 2
                    elif not rendered_segments: # Not centering, and no specific segments rendered
                         x_pos = x_pos_start # Reset to original starting x_pos for this line

                    surface.blit(remaining_surface, (x_pos, y_pos))
            else:
                # Original single-color rendering
                text_surface = current_font.render(text, True, line.get("color", self.default_color))
                y_pos = base_pos[1] - ((len(self.lines) - 1 - i) * self.line_height)
                x_pos_current = base_pos[0]
                if center_line:
                    x_pos_current = (surface.get_width() - text_surface.get_width()) // 2
                surface.blit(text_surface, (x_pos_current, y_pos))
    
    def clear(self):
        """Clear all lines from the terminal"""
        self.lines = []
        self.target_y_positions = []
        self.current_y_positions = []
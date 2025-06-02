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
        
    def add_line(self, text, animate_dots=False, color=TERMINAL_GREEN):
        """Add a new line to the terminal with position tracking and color"""
        # Shift existing lines' target positions up
        for i in range(len(self.target_y_positions)):
            self.target_y_positions[i] = i * self.line_height
            
        # Add new line at the bottom
        self.lines.append({
            "text": text,
            "animate_dots": animate_dots,
            "color": color
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
            
            # Handle colored text segments
            if isinstance(line.get("color"), dict):
                # Calculate base position for this line
                y_pos = base_pos[1] - ((len(self.lines) - 1 - i) * self.line_height)
                x_pos = base_pos[0]
                
                # Default color for non-specified segments
                default_color = line.get("default_color", self.default_color)
                
                # Split text and render each segment
                current_pos = 0
                for segment, color in line["color"].items():
                    # Find segment position
                    start_idx = text.find(segment, current_pos)
                    if start_idx != -1:
                        # Render any text before this segment with default color
                        if start_idx > current_pos:
                            before_text = text[current_pos:start_idx]
                            before_surface = self.font.render(before_text, True, default_color)
                            surface.blit(before_surface, (x_pos, y_pos))
                            x_pos += before_surface.get_width()
                        
                        # Render colored segment
                        segment_surface = self.font.render(segment, True, color)
                        surface.blit(segment_surface, (x_pos, y_pos))
                        x_pos += segment_surface.get_width()
                        current_pos = start_idx + len(segment)
                
                # Render any remaining text with default color
                if current_pos < len(text):
                    remaining_text = text[current_pos:]
                    remaining_surface = self.font.render(remaining_text, True, default_color)
                    surface.blit(remaining_surface, (x_pos, y_pos))
            else:
                # Original single-color rendering
                text_surface = self.font.render(text, True, line.get("color", self.default_color))
                y_pos = base_pos[1] - ((len(self.lines) - 1 - i) * self.line_height)
                surface.blit(text_surface, (base_pos[0], y_pos))
    
    def clear(self):
        """Clear all lines from the terminal"""
        self.lines = []
        self.target_y_positions = []
        self.current_y_positions = []
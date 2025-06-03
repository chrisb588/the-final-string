import pygame
import os

class HUD:
    """Manages the heads-up display elements"""
    
    def __init__(self, screen):
        self.screen = screen
        self.show_speed_debug = False
        self.show_coordinates = False
        self._init_font()

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
                self.font = pygame.font.Font(font_path, 32)
                self.small_font = pygame.font.Font(font_path, 20)
            else:
                print(f"Warning: Font file not found at {font_path}")
                self.font = pygame.font.Font(None, 32)
        except (pygame.error, IOError) as e:
            print(f"Warning: Could not initialize font: {e}")
            self.font = pygame.font.SysFont('arial', 32)
     
    def draw_speed_indicator(self, speed: float):
        """Draw the speed indicator"""
        if not self.show_speed_debug:
            return
            
        speed_text = f"Speed: {speed:.1f}"
        text_surface = self.font.render(speed_text, True, (255, 255, 255))
        outline_surface = self.font.render(speed_text, True, (0, 0, 0))
        
        x_pos = self.screen.get_width() - text_surface.get_width() - 20
        y_pos = 20
        
        self.screen.blit(outline_surface, (x_pos + 1, y_pos + 1))
        self.screen.blit(text_surface, (x_pos, y_pos))
        
    def draw_zoom_indicator(self, zoom: float):
        """Draw the zoom level indicator"""
        zoom_text = f"Zoom: {zoom:.1f}x"
        text_surface = self.font.render(zoom_text, True, (255, 255, 255))
        outline_surface = self.font.render(zoom_text, True, (0, 0, 0))
        
        x_pos = self.screen.get_width() - text_surface.get_width() - 20
        y_pos = 50 if self.show_speed_debug else 20
        
        self.screen.blit(outline_surface, (x_pos + 1, y_pos + 1))
        self.screen.blit(text_surface, (x_pos, y_pos))
        
    def draw_instructions(self):
        """Draw control instructions"""
        instructions = [
            "WASD/Arrow Keys: Move player",
            "Shift + Movement: Run (2x speed)",
            "N/Right: Next level",
            "P/Left: Previous level", 
            "R: Reload level",
            "+/=: Zoom in",
            "-: Zoom out", 
            "0: Reset zoom",
            "F1: Toggle debug info",
            "F2: Toggle smooth camera",
            "F3: Toggle coordinates",
            "F4: Toggle creation mode",
            "TAB: Switch note/door/delete mode (in creation mode)",
            "F5: Toggle speed debug",
            "Space: Pause",
            "1-3: Toggle layers (demo)",
            "E: Interact with objects",
            "C: Clear rules for testing",
            "I: Show interactables info (when coords shown)",
            "X: Copy mouse coords to console (when coords shown)",
            "Z: Force reload level from file (when coords shown)",
            "Delete: Clean up duplicate interactables (when coords shown)",
            "[ / ]: Decrease/Increase speed (when speed debug on)",
            "\\: Reset speed to default (when speed debug on)",
            "ESC: Quit",
            "",
            "COMPASS: Points to nearest door (top-right)",
            "- Red arrow when doors exist",
            "- N/S/E/W when no doors"
        ]
        
        y_pos = self.screen.get_height() - len(instructions) * 22 - 10
        
        for instruction in instructions:
            text_surface = self.small_font.render(instruction, True, (255, 255, 255))
            outline_surface = self.small_font.render(instruction, True, (0, 0, 0))
            
            self.screen.blit(outline_surface, (11, y_pos + 1))
            self.screen.blit(text_surface, (10, y_pos))
            y_pos += 22

    def render(self, speed: float = None, zoom: float = None):
        """Render all HUD elements"""
        try:
            # Draw speed indicator if debug is enabled
            if self.show_speed_debug and speed is not None:
                self.draw_speed_indicator(speed)
            
            # Draw zoom indicator if zoom value is provided
            if zoom is not None:
                self.draw_zoom_indicator(zoom)
            
            # Draw instructions (always visible) - COMMENTED OUT to remove from screen
            # self.draw_instructions()
            
        except Exception as e:
            print(f"Error rendering HUD: {e}")
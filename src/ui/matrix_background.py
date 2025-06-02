import pygame
import os
from PIL import Image

class MatrixBackground:
    """Background that displays a GIF image"""
    
    def __init__(self, screen_width: int, screen_height: int, gif_path: str = None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Default fallback color
        self.fallback_color = (0, 0, 0)  # Black background
        
        # GIF handling
        self.gif_surface = None
        self.gif_frames = []
        self.current_frame = 0
        self.frame_duration = 100  # milliseconds per frame
        self.last_frame_time = pygame.time.get_ticks()
        
        # Try to load the GIF
        if gif_path and os.path.exists(gif_path):
            self.load_gif(gif_path)
        else:
            print(f"GIF not found at {gif_path}, using fallback color")
    
    def load_gif(self, gif_path: str):
        """Load a GIF file and convert frames to pygame surfaces"""
        try:
            # Open the GIF with PIL
            gif = Image.open(gif_path)
            
            # Extract all frames
            frames = []
            try:
                while True:
                    # Convert frame to RGB (in case it's in palette mode)
                    frame = gif.convert('RGB')
                    
                    # Resize frame to screen size
                    frame = frame.resize((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
                    
                    # Convert PIL image to pygame surface
                    frame_data = frame.tobytes()
                    pygame_surface = pygame.image.fromstring(frame_data, frame.size, 'RGB')
                    frames.append(pygame_surface)
                    
                    # Move to next frame
                    gif.seek(gif.tell() + 1)
            except EOFError:
                # End of frames
                pass
            
            if frames:
                self.gif_frames = frames
                self.gif_surface = frames[0]  # Start with first frame
                
                # Try to get frame duration from GIF
                try:
                    self.frame_duration = gif.info.get('duration', 100)
                except:
                    self.frame_duration = 100  # Default 100ms per frame
                
                print(f"Loaded GIF with {len(frames)} frames, {self.frame_duration}ms per frame")
            else:
                print("No frames found in GIF")
                
        except Exception as e:
            print(f"Error loading GIF: {e}")
            self.gif_frames = []
            self.gif_surface = None
    
    def update(self):
        """Update the animation frame if it's an animated GIF"""
        if len(self.gif_frames) > 1:  # Only animate if multiple frames
            current_time = pygame.time.get_ticks()
            if current_time - self.last_frame_time >= self.frame_duration:
                self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
                self.gif_surface = self.gif_frames[self.current_frame]
                self.last_frame_time = current_time
    
    def render(self, screen: pygame.Surface):
        """Render the background"""
        if self.gif_surface:
            # Draw the GIF frame
            screen.blit(self.gif_surface, (0, 0))
        else:
            # Fallback to solid color
            screen.fill(self.fallback_color)
    
    def resize(self, new_width: int, new_height: int, gif_path: str = None):
        """Handle screen resize by reloading the GIF at new size"""
        self.screen_width = new_width
        self.screen_height = new_height
        
        # Reload GIF at new size if we have a path
        if gif_path and os.path.exists(gif_path):
            self.load_gif(gif_path) 
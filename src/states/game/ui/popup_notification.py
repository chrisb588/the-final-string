import pygame
import os

class PopupNotification:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.messages = []  # List of {text, duration, start_time, alpha}
        self._init_font()
        
    def _init_font(self):
        """Initialize font with fallback"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            main_dir = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
            font_path = os.path.join(main_dir, 'assets', 'fonts', 'UnifontEX.ttf')
            
            if os.path.exists(font_path):
                self.font = pygame.font.Font(font_path, 16)
            else:
                self.font = pygame.font.Font(None, 16)
        except Exception as e:
            print(f"Warning: Could not initialize PopupNotification font: {e}")
            self.font = pygame.font.Font(None, 16)
    
    def show(self, text: str, duration: int = 2000):
        """Add a new popup message"""
        self.messages.append({
            'text': text,
            'duration': duration,
            'start_time': pygame.time.get_ticks(),
            'alpha': 255  # Start fully opaque
        })
    
    def update(self):
        """Update message timers and fade out"""
        current_time = pygame.time.get_ticks()
        
        # Update each message
        for msg in self.messages[:]:  # Create a copy to iterate
            elapsed = current_time - msg['start_time']
            
            # Start fading out in the last 500ms
            if elapsed > (msg['duration'] - 500):
                fade_progress = (elapsed - (msg['duration'] - 500)) / 500
                msg['alpha'] = max(0, int(255 * (1 - fade_progress)))
            
            # Remove expired messages
            if elapsed >= msg['duration']:
                self.messages.remove(msg)
    
    def render(self):
        """Render active popup messages"""
        if not self.messages:
            return
            
        screen_width = self.screen.get_width()
        base_y = self.screen.get_height() - 100  # Start from bottom
        
        # Render each message from bottom to top
        for i, msg in enumerate(reversed(self.messages)):
            text_surface = self.font.render(msg['text'], True, (230, 230, 240))
            text_rect = text_surface.get_rect()
            
            # Create background surface with alpha
            bg_surface = pygame.Surface((text_rect.width + 20, text_rect.height + 10))
            bg_surface.set_alpha(int(msg['alpha'] * 0.8))  # Slightly more transparent than text
            bg_surface.fill((45, 45, 55))
            
            # Position at bottom right with padding
            x = screen_width - text_rect.width - 30
            y = base_y - (i * (text_rect.height + 15))  # Stack messages upward
            
            # Draw background with border
            bg_rect = pygame.Rect(x - 10, y - 5, text_rect.width + 20, text_rect.height + 10)
            self.screen.blit(bg_surface, bg_rect)
            pygame.draw.rect(self.screen, (80, 80, 90), bg_rect, 2, border_radius=5)
            
            # Draw text with alpha
            text_surface.set_alpha(msg['alpha'])
            self.screen.blit(text_surface, (x, y))
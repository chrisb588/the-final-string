import pygame
from typing import Tuple

class Player:
    def __init__(self, x: int = 100, y: int = 100):
        self.x = x
        self.y = y
        self.speed = 2.0
        self.min_speed = 0.5
        self.max_speed = 10.0
        self.speed_increment = 0.5
        self.color = (255, 100, 100)  # Red-ish color
        
    def move(self, keys: pygame.key.ScancodeWrapper, level_manager) -> None:
        """Handle player movement with collision detection"""
        old_x, old_y = self.x, self.y
        
        # Check if shift is held for running
        is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        current_speed = self.speed * 1.5 if is_running else self.speed
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.y -= current_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.y += current_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x -= current_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x += current_speed
            
        # Check collision and revert if needed
        if level_manager.check_collision(self.x, self.y):
            self.x, self.y = old_x, old_y
            
    def get_position(self) -> Tuple[int, int]:
        """Get current player position"""
        return (self.x, self.y)
        
    def set_position(self, x: int, y: int) -> None:
        """Set player position"""
        self.x = x
        self.y = y
        
    def get_tile_position(self) -> Tuple[int, int]:
        """Get player position in tile coordinates"""
        return (int(self.x // 16), int(self.y // 16))
        
    def adjust_speed(self, increment: float) -> None:
        """Adjust player speed within bounds"""
        new_speed = self.speed + increment
        self.speed = max(self.min_speed, min(new_speed, self.max_speed))
        
    def reset_speed(self) -> None:
        """Reset speed to default"""
        self.speed = 2.0
        
    def render(self, screen: pygame.Surface, camera) -> None:
        """Render the player"""
        player_screen_x, player_screen_y = camera.apply(self.x, self.y)
        zoom = camera.zoom
        player_radius = int(8 * zoom)
        
        pygame.draw.circle(
            screen,
            self.color,
            (int(player_screen_x * zoom), int(player_screen_y * zoom)),
            player_radius
        )
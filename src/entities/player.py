import pygame
from typing import Tuple

class Player:
    # Animation states
    IDLE = "idle"
    WALKING = "walking"
    RUNNING = "running"
    
    # Facing directions
    FRONT = "front"
    BACK = "back"
    RIGHT = "right"
    LEFT = "left"

    def __init__(self, x: int = 100, y: int = 100):
        self.x = x
        self.y = y
        self.speed = 2.0
        self.min_speed = 0.5
        self.max_speed = 10.0
        self.speed_increment = 0.5
        
        # Animation properties
        self.spritesheets = {
            self.IDLE: pygame.image.load("assets/images/sprites/player/idle.png").convert_alpha(),
            self.WALKING: pygame.image.load("assets/images/sprites/player/walk.png").convert_alpha(),
            self.RUNNING: pygame.image.load("assets/images/sprites/player/run.png").convert_alpha()
        }
        # Animation properties
        self.animation_speeds = {
            self.IDLE: 150,     # Slower for idle
            self.WALKING: 100,  # Faster for walking
            self.RUNNING: 80    # Even faster for running
        }
        self.animation_speed = self.animation_speeds[self.IDLE]  # Start with idle speed
        self.frame_width = 16  # Width of each frame
        self.frame_height = 16  # Height of each frame
        self.animation_frames = {}
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 150  # milliseconds per frame
        self.current_state = self.IDLE
        self.facing = self.FRONT
        self.last_update = pygame.time.get_ticks()
        
        # Load all animations
        self.load_animations()

    def load_animations(self):
        """Load all animation frames from separate spritesheets"""
        # Define frame counts for each animation state
        frame_counts = {
            self.IDLE: 4,
            self.WALKING: 8,
            self.RUNNING: 8
        }
        
        # Define row indices for each direction
        direction_rows = {
            self.RIGHT: 0,
            self.FRONT: 1,
            self.BACK: 2
        }
        
        # Initialize animation frames dictionary
        self.animation_frames = {
            self.IDLE: {},
            self.WALKING: {},
            self.RUNNING: {}
        }
        
        # Load frames for each state from its respective spritesheet
        for state in [self.IDLE, self.WALKING, self.RUNNING]:
            spritesheet = self.spritesheets[state]
            
            for direction, row in direction_rows.items():
                frames = []
                for frame in range(frame_counts[state]):
                    # Calculate position in spritesheet
                    x = frame * self.frame_width
                    y = row * self.frame_height
                    
                    # Extract frame from spritesheet
                    frame_surface = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
                    frame_surface.blit(spritesheet, (0, 0), (x, y, self.frame_width, self.frame_height))
                    
                    frames.append(frame_surface)
                    
                    # For LEFT direction, flip the RIGHT frames horizontally
                    if direction == self.RIGHT:
                        left_frame = pygame.transform.flip(frame_surface, True, False)
                        if self.LEFT not in self.animation_frames[state]:
                            self.animation_frames[state][self.LEFT] = []
                        self.animation_frames[state][self.LEFT].append(left_frame)
                
                self.animation_frames[state][direction] = frames
    
    def update_animation_state(self, keys: pygame.key.ScancodeWrapper):
        """Update animation state based on movement"""
        # Store previous state to handle transitions
        previous_state = self.current_state
        previous_facing = self.facing
        
        # Update facing direction first (to preserve last direction when idle)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.facing = self.RIGHT
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.facing = self.LEFT
        elif keys[pygame.K_w] or keys[pygame.K_UP]:
            self.facing = self.BACK
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.facing = self.FRONT
            
        # Determine if moving
        is_moving = any([
            keys[pygame.K_w], keys[pygame.K_s],
            keys[pygame.K_a], keys[pygame.K_d],
            keys[pygame.K_UP], keys[pygame.K_DOWN],
            keys[pygame.K_LEFT], keys[pygame.K_RIGHT]
        ])
        
        # Determine if running
        is_running = is_moving and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
        
        # Update state
        if not is_moving:
            self.current_state = self.IDLE
        elif is_running:
            self.current_state = self.RUNNING
        else:
            self.current_state = self.WALKING

        # Handle state transitions
        if previous_state != self.current_state or previous_facing != self.facing:
            # Ensure we have valid frames for the new state/direction
            if (self.current_state in self.animation_frames and 
                self.facing in self.animation_frames[self.current_state]):
                # Reset frame only if we have valid frames for the new state
                total_frames = len(self.animation_frames[self.current_state][self.facing])
                if total_frames > 0:
                    # Keep frame index within valid range for new animation
                    self.current_frame = min(self.current_frame, total_frames - 1)
                    self.last_update = pygame.time.get_ticks()  # Reset animation timer
            else:
                # If no valid frames, keep previous state/facing
                self.current_state = previous_state
                self.facing = previous_facing

        # Update animation speed based on state
        self.animation_speed = self.animation_speeds[self.current_state]
    
    def update_animation(self):
        """Update animation frame"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.animation_speed:
            if (self.current_state in self.animation_frames and 
                self.facing in self.animation_frames[self.current_state] and 
                len(self.animation_frames[self.current_state][self.facing]) > 0):
                
                self.current_frame = (self.current_frame + 1) % len(self.animation_frames[self.current_state][self.facing])
                self.last_update = current_time
        
    def move(self, keys: pygame.key.ScancodeWrapper, level_manager) -> None:
        """Handle player movement with collision detection"""
        old_x, old_y = self.x, self.y

        # Update animation state first
        self.update_animation_state(keys)
        
        # Check if shift is held for running
        is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        current_speed = self.speed * 1.5 if is_running else self.speed
        
        # Calculate movement deltas
        dx = 0
        dy = 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= current_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += current_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= current_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += current_speed
        
        # Try X movement first
        if dx != 0:
            self.x += dx
            if level_manager.check_collision(self.x, self.y):
                self.x = old_x  # Revert only X movement
        
        # Try Y movement separately
        if dy != 0:
            self.y += dy
            if level_manager.check_collision(self.x, self.y):
                self.y = old_y  # Revert only Y movement

        # Update animation frame
        self.update_animation()
            
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
        """Render the player with current animation frame and shadow"""
        player_screen_x, player_screen_y = camera.apply(self.x, self.y)
        zoom = camera.zoom
        
        # Draw shadow first (beneath the player)
        self._draw_shadow(screen, player_screen_x, player_screen_y, zoom)
        
        try:
            # Safely get current animation frame
            if (self.current_state in self.animation_frames and 
                self.facing in self.animation_frames[self.current_state] and 
                len(self.animation_frames[self.current_state][self.facing]) > 0):
                
                current_frame = self.animation_frames[self.current_state][self.facing][self.current_frame]
                
                # Scale frame if needed
                if zoom != 1.0:
                    scaled_width = int(self.frame_width * zoom)
                    scaled_height = int(self.frame_height * zoom)
                    current_frame = pygame.transform.scale(current_frame, (scaled_width, scaled_height))
                
                # Draw frame
                screen.blit(
                    current_frame,
                    (
                        int(player_screen_x * zoom - current_frame.get_width()//2),
                        int(player_screen_y * zoom - current_frame.get_height()//2)
                    )
                )
            else:
                # Fallback: draw a simple colored rectangle if no animation frame available
                size = int(16 * zoom)
                pygame.draw.rect(
                    screen,
                    (255, 100, 100),  # Red-ish color
                    (
                        int(player_screen_x * zoom - size//2),
                        int(player_screen_y * zoom - size//2),
                        size,
                        size
                    )
                )
        except Exception as e:
            print(f"Error rendering player: {e}")
            # Fallback rendering
            size = int(16 * zoom)
            pygame.draw.rect(
                screen,
                (255, 100, 100),  # Red-ish color
                (
                    int(player_screen_x * zoom - size//2),
                    int(player_screen_y * zoom - size//2),
                    size,
                    size
                )
            )
    
    def _draw_shadow(self, screen: pygame.Surface, player_screen_x: float, player_screen_y: float, zoom: float) -> None:
        """Draw a shadow beneath the player"""
        # Shadow properties
        shadow_width = int(14 * zoom)  # Slightly smaller than player
        shadow_height = int(6 * zoom)  # Flattened oval
        shadow_offset_y = int(6 * zoom)  # Offset down from player center
        shadow_alpha = 80  # Semi-transparent (0-255)
        
        # Calculate shadow position (centered horizontally, offset down vertically)
        shadow_x = int(player_screen_x * zoom - shadow_width // 2)
        shadow_y = int(player_screen_y * zoom - shadow_height // 2 + shadow_offset_y)
        
        # Create a surface for the shadow with alpha support
        shadow_surface = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
        
        # Draw the shadow as a dark oval
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, shadow_alpha), shadow_surface.get_rect())
        
        # Blit the shadow to the screen
        screen.blit(shadow_surface, (shadow_x, shadow_y))
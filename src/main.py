import pygame
import sys
from levels.manager import LayeredLevelManager

class GameDemo:
    """Demo showing the layered tileset renderer in action"""
    
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        
        # Screen setup
        self.screen_width = 1024
        self.screen_height = 572
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Layered Tileset Renderer Demo")
        
        # Clock for FPS control
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Initialize level manager with layered rendering
        self.level_manager = LayeredLevelManager(
            self.screen, 
            sprite_sheet_path="assets/images/spritesheets"
        )
        
        # Player for camera following (simple representation)
        self.player_x = 100
        self.player_y = 100
        self.player_speed = 3
        
        # Debug and control flags
        self.show_debug = False
        self.smooth_camera = True
        self.paused = False
        
        # Try to load first level
        if not self.level_manager.load_first_level():
            print("No levels found! Make sure your level files are in the correct directory.")
    
    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                # Level navigation
                if event.key == pygame.K_n or event.key == pygame.K_RIGHT:
                    self.level_manager.load_next_level()
                
                elif event.key == pygame.K_p or event.key == pygame.K_LEFT:
                    self.level_manager.load_previous_level()
                
                elif event.key == pygame.K_r:
                    # Reload current level
                    current_name = self.level_manager.current_level_name
                    if current_name:
                        self.level_manager.load_level(current_name)
                
                # Debug toggles
                elif event.key == pygame.K_F1:
                    self.show_debug = not self.show_debug
                
                elif event.key == pygame.K_F2:
                    self.smooth_camera = not self.smooth_camera
                
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                
                # Layer visibility toggles (for testing)
                elif event.key == pygame.K_1:
                    # Toggle ground layer
                    self._toggle_layer("ground")
                
                elif event.key == pygame.K_2:
                    # Toggle walls layer
                    self._toggle_layer("walls")
                
                elif event.key == pygame.K_3:
                    # Toggle objects layer
                    self._toggle_layer("objects-collision")
        
        return True
    
    def _toggle_layer(self, layer_name: str):
        """Toggle visibility of a specific layer (demo feature)"""
        # This is a simple implementation - you'd want to track layer states properly
        print(f"Layer toggle for '{layer_name}' - implement layer visibility tracking as needed")
    
    def update(self):
        """Update game state"""
        if self.paused:
            return
        
        # Handle player movement
        keys = pygame.key.get_pressed()
        old_x, old_y = self.player_x, self.player_y
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.player_y -= self.player_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.player_y += self.player_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.player_x -= self.player_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.player_x += self.player_speed
        
        # Check collision and revert if needed
        if self.level_manager.check_collision(self.player_x, self.player_y):
            self.player_x, self.player_y = old_x, old_y
        
        # Update camera to follow player
        self.level_manager.update_camera(
            self.player_x, self.player_y, 
            smooth=self.smooth_camera
        )
    
    def render(self):
        """Render the game"""
        # Clear screen
        self.screen.fill((64, 128, 255))  # Sky blue background
        
        # Render level with layered sprites
        self.level_manager.render_level(debug_info=self.show_debug)
        
        # Draw player (simple representation)
        player_screen_x, player_screen_y = self.level_manager.camera.apply(
            self.player_x, self.player_y
        )
        pygame.draw.circle(
            self.screen, 
            (255, 100, 100), 
            (int(player_screen_x), int(player_screen_y)), 
            8
        )
        
        # Draw control instructions
        self._draw_instructions()
        
        # Update display
        pygame.display.flip()
    
    def _draw_instructions(self):
        """Draw control instructions on screen"""
        font = pygame.font.Font(None, 20)
        instructions = [
            "WASD/Arrow Keys: Move player",
            "N/Right: Next level",
            "P/Left: Previous level", 
            "R: Reload level",
            "F1: Toggle debug info",
            "F2: Toggle smooth camera",
            "Space: Pause",
            "1-3: Toggle layers (demo)",
            "ESC: Quit"
        ]
        
        y_pos = self.screen_height - len(instructions) * 22 - 10
        
        for instruction in instructions:
            # Draw with outline for visibility
            text_surface = font.render(instruction, True, (255, 255, 255))
            outline_surface = font.render(instruction, True, (0, 0, 0))
            
            self.screen.blit(outline_surface, (11, y_pos + 1))
            self.screen.blit(text_surface, (10, y_pos))
            y_pos += 22
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Handle events
            running = self.handle_events()
            
            # Update game state
            self.update()
            
            # Render
            self.render()
            
            # Control frame rate
            self.clock.tick(self.fps)
            
            # Update window title with FPS
            fps = self.clock.get_fps()
            level_info = self.level_manager.get_level_info()
            pygame.display.set_caption(
                f"Layered Tileset Demo - FPS: {fps:.1f} - "
                f"Level: {level_info.get('name', 'None')} - "
                f"Sprites: {level_info.get('visible_sprites', 0)}/{level_info.get('total_sprites', 0)}"
            )
        
        pygame.quit()
        sys.exit()

def game_state():
    """Entry point"""
    try:
        demo = GameDemo()
        demo.run()
    except Exception as e:
        print(f"Error running demo: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    game_state()
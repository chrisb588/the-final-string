import pygame
import sys
from typing import Dict, Any
from levels.manager import LayeredLevelManager
from game_state import game_state
from entities.interactables import interactable_manager
from ui.password_ui import PasswordUI, MessageUI, RulesDisplayUI

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
        
        # UI components
        self.password_ui = PasswordUI(self.screen)
        self.message_ui = MessageUI(self.screen)
        self.rules_ui = RulesDisplayUI(self.screen)
        
        # Interaction callback not needed - handled directly in interact_with_objects
        
        # Try to load first level
        if not self.level_manager.load_first_level():
            print("No levels found! Make sure your level files are in the correct directory.")
        else:
            # Set player to starting point of the level
            self.player_x, self.player_y = self.level_manager.get_level_starting_point()
            self.load_level_interactables()
    
    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Let password UI handle events first
            if self.password_ui.handle_event(event):
                continue
            
            elif event.type == pygame.KEYDOWN:
                # Level navigation
                if event.key == pygame.K_n or event.key == pygame.K_RIGHT:
                    if self.level_manager.load_next_level():
                        # Move player to starting point of new level
                        self.player_x, self.player_y = self.level_manager.get_level_starting_point()
                        self.load_level_interactables()
                
                elif event.key == pygame.K_p or event.key == pygame.K_LEFT:
                    if self.level_manager.load_previous_level():
                        # Move player to starting point of new level
                        self.player_x, self.player_y = self.level_manager.get_level_starting_point()
                        self.load_level_interactables()
                
                elif event.key == pygame.K_r:
                    # Reload current level
                    current_name = self.level_manager.current_level_name
                    if current_name:
                        if self.level_manager.load_level(current_name):
                            # Move player to starting point
                            self.player_x, self.player_y = self.level_manager.get_level_starting_point()
                            self.load_level_interactables()
                
                # Debug toggles
                elif event.key == pygame.K_F1:
                    self.show_debug = not self.show_debug
                
                elif event.key == pygame.K_F2:
                    self.smooth_camera = not self.smooth_camera
                
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                
                # Zoom controls
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    # Zoom in
                    self.level_manager.camera.zoom_in()
                
                elif event.key == pygame.K_MINUS:
                    # Zoom out
                    self.level_manager.camera.zoom_out()
                
                elif event.key == pygame.K_0:
                    # Reset zoom to normal
                    self.level_manager.camera.set_zoom(1.0)
                
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
                
                # Interaction
                elif event.key == pygame.K_e:
                    # Interact with objects
                    self.interact_with_objects()
                
                elif event.key == pygame.K_c:
                    # Clear rules for testing
                    game_state.clear_rules_for_testing()
                    self.message_ui.show_message("Rules cleared for testing!", 2000)
        
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
        
        # Update UI components
        self.message_ui.update()
        
        # Check for nearby interactables
        self.check_nearby_interactables()
    
    def render(self):
        """Render the game"""
        # Clear screen
        self.screen.fill((64, 128, 255))  # Sky blue background
        
        # Render level with layered sprites
        self.level_manager.render_level(debug_info=self.show_debug)
        
        # Draw player (simple representation) - account for zoom
        player_screen_x, player_screen_y = self.level_manager.camera.apply(
            self.player_x, self.player_y
        )
        # Scale player size with zoom
        zoom = self.level_manager.camera.zoom
        player_radius = int(8 * zoom)
        pygame.draw.circle(
            self.screen, 
            (255, 100, 100), 
            (int(player_screen_x * zoom), int(player_screen_y * zoom)), 
            player_radius
        )
        
        # Draw zoom level indicator
        self._draw_zoom_indicator()
        
        # Draw control instructions
        self._draw_instructions()
        
        # Render UI components
        self.rules_ui.render(game_state.get_rules())
        self.message_ui.render()
        self.password_ui.render()
        
        # Update display
        pygame.display.flip()
    
    def _draw_zoom_indicator(self):
        """Draw zoom level indicator in top-right corner"""
        font = pygame.font.Font(None, 32)
        zoom = self.level_manager.camera.zoom
        zoom_text = f"Zoom: {zoom:.1f}x"
        
        # Render text with outline for visibility
        text_surface = font.render(zoom_text, True, (255, 255, 255))
        outline_surface = font.render(zoom_text, True, (0, 0, 0))
        
        # Position in top-right corner
        text_width = text_surface.get_width()
        x_pos = self.screen_width - text_width - 20
        y_pos = 20
        
        # Draw outline and text
        self.screen.blit(outline_surface, (x_pos + 1, y_pos + 1))
        self.screen.blit(text_surface, (x_pos, y_pos))
    
    def _draw_instructions(self):
        """Draw control instructions on screen"""
        font = pygame.font.Font(None, 20)
        instructions = [
            "WASD/Arrow Keys: Move player",
            "N/Right: Next level",
            "P/Left: Previous level", 
            "R: Reload level",
            "+/=: Zoom in",
            "-: Zoom out", 
            "0: Reset zoom",
            "F1: Toggle debug info",
            "F2: Toggle smooth camera",
            "Space: Pause",
            "1-3: Toggle layers (demo)",
            "E: Interact with objects",
            "C: Clear rules for testing",
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
    
    def load_level_interactables(self):
        """Load interactables for the current level"""
        if self.level_manager.current_level:
            interactable_manager.load_from_level_data(self.level_manager.current_level.raw_data)
    
    def check_nearby_interactables(self):
        """Check for nearby interactables and show interaction hints"""
        # Convert player position to tile coordinates
        player_tile_x = int(self.player_x // 16)
        player_tile_y = int(self.player_y // 16)
        
        # Check adjacent tiles for interactables
        adjacent_positions = [
            (player_tile_x, player_tile_y),      # Current tile
            (player_tile_x - 1, player_tile_y),  # Left
            (player_tile_x + 1, player_tile_y),  # Right
            (player_tile_x, player_tile_y - 1),  # Up
            (player_tile_x, player_tile_y + 1),  # Down
        ]
        
        for tile_x, tile_y in adjacent_positions:
            obj = interactable_manager.get_interactable_at(tile_x, tile_y)
            if obj:
                # Could show interaction prompt here
                break
    
    def interact_with_objects(self):
        """Interact with nearby objects"""
        # Convert player position to tile coordinates
        player_tile_x = int(self.player_x // 16)
        player_tile_y = int(self.player_y // 16)
        
        # Check adjacent tiles for interactables
        adjacent_positions = [
            (player_tile_x, player_tile_y),      # Current tile
            (player_tile_x - 1, player_tile_y),  # Left
            (player_tile_x + 1, player_tile_y),  # Right
            (player_tile_x, player_tile_y - 1),  # Up
            (player_tile_x, player_tile_y + 1),  # Down
        ]
        
        for tile_x, tile_y in adjacent_positions:
            result = interactable_manager.interact_at(tile_x, tile_y, self.player_x, self.player_y)
            if result.get("type") != "none":
                self.handle_interaction(result)
                break
    
    def handle_interaction(self, result: Dict[str, Any]):
        """Handle interaction results"""
        interaction_type = result.get("type", "none")
        
        if interaction_type == "note_collected":
            message = result.get("message", "Note collected!")
            self.message_ui.show_message(message, 3000)
            
        elif interaction_type == "note_already_collected":
            message = result.get("message", "Already read this note.")
            self.message_ui.show_message(message, 2000)
            
        elif interaction_type == "door_locked":
            message = result.get("message", "Door is locked.")
            self.message_ui.show_message(message, 3000)
            
        elif interaction_type == "door_password_prompt":
            # Show password UI
            rules = result.get("rules", [])
            collected_rules = result.get("collected_rules", [])
            door = result.get("door")
            self.password_ui.show(rules, door, self.handle_password_result, collected_rules)
            
        elif interaction_type == "door_open":
            message = result.get("message", "Door is open.")
            self.message_ui.show_message(message, 2000)
    
    def handle_password_result(self, result: Dict[str, Any]):
        """Handle password attempt results"""
        if result.get("success", False):
            self.message_ui.show_message("Door opened successfully!", 3000)
        else:
            message = result.get("message", "Password incorrect.")
            self.message_ui.show_message(message, 3000)
    
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

def main():
    """Entry point"""
    try:
        demo = GameDemo()
        demo.run()
    except Exception as e:
        print(f"Error running demo: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()
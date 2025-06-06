import pygame
import sys
import math
import random
import os
from typing import Dict, Any, Set, Tuple, List

# Add src directory to path so we can import modules
src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from levels.manager import LayeredLevelManager
from rules import game_state
from entities.interactables import interactable_manager
from states.game.ui.ui_manager import UIManager
from entities.player import Player
from ui.crt_filter import CRTFilter

class GameDemo:
    """Demo showing the layered tileset renderer in action"""
    
    def __init__(self, screen=None):
        # Initialize Pygame if not already done
        if not pygame.get_init():
            pygame.init()

        if screen is not None:
            # Use provided screen (windowed mode from main.py)
            self.screen = screen
            self.screen_width = screen.get_width()
            self.screen_height = screen.get_height()
            self.is_fullscreen = False
            self.user_screen_width = self.screen_width
            self.user_screen_height = self.screen_height
            self.windowed_size = (self.screen_width, self.screen_height)  # Set windowed_size for provided screen
        else:
            # Create our own screen (for standalone execution)
            display_info = pygame.display.Info()
            self.user_screen_width = display_info.current_w
            self.user_screen_height = display_info.current_h
            self.screen_width = self.user_screen_width
            self.screen_height = self.user_screen_height
            self.is_fullscreen = True
            
            self.windowed_size = (1024, 768)
            # Create our own full screen
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        
        pygame.display.set_caption("The Final String")
        
        # Game state
        self.running = True
        self.game_completed = False  # Flag to track if level-4 is completed
        self.paused = False
        self.clock = pygame.time.Clock()
        self.fps = 60  # Target FPS for game loop
        self.dt = 0.0
        
        # Debug and creation mode variables
        self.show_debug = False
        self.show_speed_debug = False
        self.show_coordinates = False  # Debug coordinate display
        self.smooth_camera = True  # Camera smoothing setting
        self.creation_mode = False
        self.creation_type = "note"  # "note", "door"
        self.delete_mode = False
        self.selected_tiles = set()  # Track selected tiles for multi-tile interactables
        
        # Mouse tracking for debug coordinates
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_tile_x = 0
        self.mouse_tile_y = 0
        
        # Initialize level manager with layered rendering
        self.level_manager = LayeredLevelManager(
            self.screen, 
            sprite_sheet_path="assets/images/spritesheets"
        )

        # Replace player variables with Player instance
        self.player = Player()

        # Level transition persistence
        self.last_successful_password = ""
        self.is_transitioning = False
        self.accumulated_rules = []  # Rules from all previously completed levels
        self.used_rules = set()     # Add this line to initialize used_rules tracking

        # Load first level and set initial player position
        if self.level_manager.load_level("level-0"):
            start_x, start_y = self.level_manager.get_level_starting_point()
            self.player.set_position(start_x, start_y)
            self.load_level_interactables()
        else:
            print("Could not load level-0! Trying to load first available level...")
            if self.level_manager.load_first_level():
                start_x, start_y = self.level_manager.get_level_starting_point()
                self.player.set_position(start_x, start_y)
                self.load_level_interactables()
            else:
                print("No levels found! Make sure your level files are in the correct directory.")
        
        self.ui_manager = UIManager(self.screen)
        
        # Set initial debug flags for UI manager
        self.ui_manager.set_debug_flags(
            show_debug=self.show_debug,
            show_coordinates=self.show_coordinates,
            show_speed_debug=self.show_speed_debug
        )
        
        # # Matrix background
        # self.matrix_background = MatrixBackground(
        #     self.screen_width, 
        #     self.screen_height, 
        #     gif_path="assets/images/matrix_background.gif"  # You can change this path
        # )
        
        # Level transition persistence
        self.last_successful_password = ""
        self.is_transitioning = False
        self.accumulated_rules = []  # Rules from all previously completed levels
        self.used_rules = set()  # Track rules that have been used in any level
        self.current_level_rules = []  # Rules found in the current level only (resets each level)
        

        self.interact_sfx = pygame.mixer.Sound('assets/audio/interact.wav')
        self.interact_sfx.set_volume(0.3) 
        self.npc_sfx = pygame.mixer.Sound('assets/audio/npc.mp3')
        self.npc_sfx.set_volume(0.3)
        self.click_sfx = pygame.mixer.Sound('assets/audio/game_click.mp3')
        self.click_sfx.set_volume(0.3)
        self.success_sfx = pygame.mixer.Sound('assets/audio/success.mp3')
        self.success_sfx.set_volume(0.3)
        self.invalid_sfx = pygame.mixer.Sound('assets/audio/invalid.mp3')
        self.invalid_sfx.set_volume(0.3)
        # Removed setup_level_interactables() call since programmable setups are not being used

    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            fullscreen_size = (self.user_screen_width, self.user_screen_height)
            
            # Switch to fullscreen
            self.screen = pygame.display.set_mode(fullscreen_size, pygame.FULLSCREEN)
            self.screen_width, self.screen_height = fullscreen_size
        else:
            # Switch back to windowed mode
            self.screen = pygame.display.set_mode(self.windowed_size)
            self.screen_width, self.screen_height = self.windowed_size
        
        # Update UI components that depend on screen size
        if hasattr(self.ui_manager, 'dialogue_box'):
            self.ui_manager.dialogue_box._init_dimensions()
        
        # Show message about the change
        mode = "Fullscreen" if self.is_fullscreen else "Windowed"
        self.ui_manager.show_popup(f"Switched to {mode} mode")
    
    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.USEREVENT + 1:
                # Custom event triggered when level-4 is completed
                print("Game completion timer triggered - exiting to end video...")
                self.game_completed = True
                return False  # Exit the game loop
            
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                self.handle_resize(event.w, event.h)
            
            # Handle UI events first
            if self.ui_manager.handle_event(event):
                continue

            elif event.type == pygame.MOUSEMOTION:
                # Update mouse position for debug coordinates
                self.mouse_x, self.mouse_y = event.pos
                self._update_mouse_tile_coords()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_mouse_click(event.pos)
            
            elif event.type == pygame.KEYDOWN:
                # Handle fullscreen toggle before other keys
                if (event.key == pygame.K_RETURN and pygame.key.get_mods() & pygame.KMOD_ALT) or event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                    continue

                # Dialog and interaction handling
                if event.key == pygame.K_e:
                    if self.ui_manager.dialogue_box.is_active:
                        self.click_sfx.play()  # Play click sound when skipping/exiting dialogue
                        if self.ui_manager.dialogue_box.is_animating:
                            self.ui_manager.dialogue_box.skip_animation()  # Skip animation
                        else:
                            self.ui_manager.dialogue_box.hide()  # Close dialogue
                    elif not self.paused:
                        self.interact_with_objects()
                
                # Handle pause toggle
                elif event.key == pygame.K_ESCAPE:
                    if self.ui_manager.password_ui.visible:
                        self.click_sfx.play()
                        self.ui_manager.password_ui.hide()
                    else:
                        self.click_sfx.play()
                        self.paused = not self.paused
                    continue
                elif event.key == pygame.K_SPACE:
                    if not self.ui_manager.password_ui.visible:
                        self.click_sfx.play()
                        self.paused = not self.paused
                    continue

                # Level navigation (debug mode)
                elif (event.key == pygame.K_n or event.key == pygame.K_RIGHT) and self.ui_manager.hud.show_coordinates:
                    if self.level_manager.load_next_level():
                        start_x, start_y = self.level_manager.get_level_starting_point()
                        self.player.set_position(start_x, start_y)
                        self.load_level_interactables()
                
                elif (event.key == pygame.K_p or event.key == pygame.K_LEFT) and self.ui_manager.hud.show_coordinates:
                    if self.level_manager.load_previous_level():
                        start_x, start_y = self.level_manager.get_level_starting_point()
                        self.player.set_position(start_x, start_y)
                        self.load_level_interactables()
                
                elif event.key == pygame.K_r and self.ui_manager.hud.show_coordinates:
                    current_name = self.level_manager.current_level_name
                    if current_name:
                        if self.level_manager.load_level(current_name):
                            start_x, start_y = self.level_manager.get_level_starting_point()
                            self.player.set_position(start_x, start_y)
                            self.load_level_interactables()
                
                # Debug toggles
                elif event.key == pygame.K_F1:
                    self.show_debug = not self.show_debug
                
                elif event.key == pygame.K_F2:
                    self.smooth_camera = not self.smooth_camera
                
                elif event.key == pygame.K_F3:
                    self.ui_manager.hud.show_coordinates = not self.ui_manager.hud.show_coordinates
                
                elif event.key == pygame.K_F4:
                    self.creation_mode = not self.creation_mode
                    if not self.creation_mode:
                        self.selected_tiles.clear()
                        self.delete_mode = False
                    self.ui_manager.show_message(
                        f"Creation mode: {'ON' if self.creation_mode else 'OFF'} ({self.creation_type})", 2000
                    )
                
                elif event.key == pygame.K_TAB and self.creation_mode:
                    if self.creation_type == "note":
                        self.creation_type = "door"
                        self.delete_mode = False
                    elif self.creation_type == "door":
                        self.creation_type = "delete"
                        self.delete_mode = True
                    else:  # delete mode
                        self.creation_type = "note"
                        self.delete_mode = False
                    
                    self.selected_tiles.clear()
                    mode_text = "DELETE" if self.delete_mode else self.creation_type.upper()
                    self.ui_manager.show_message(f"Creation mode: {mode_text}", 2000)
                
                elif event.key == pygame.K_F5:
                    self.ui_manager.hud.show_speed_debug = not self.ui_manager.hud.show_speed_debug

                # Other debug functions
                elif event.key == pygame.K_c and self.ui_manager.hud.show_coordinates:
                    game_state.clear_rules_for_testing()
                    self.ui_manager.show_message("Rules cleared for testing!", 2000)
                
                elif event.key == pygame.K_i and self.ui_manager.hud.show_coordinates:
                    self._show_interactables_info()
                
                elif event.key == pygame.K_x and self.ui_manager.hud.show_coordinates:
                    self._copy_mouse_coordinates()
                
                elif event.key == pygame.K_DELETE and self.ui_manager.hud.show_coordinates:
                    self._clean_duplicate_interactables()
                
                elif event.key == pygame.K_z and self.ui_manager.hud.show_coordinates:
                    current_name = self.level_manager.current_level_name
                    if current_name and self.level_manager.load_level(current_name):
                        self.load_level_interactables()
                
                elif event.key == pygame.K_RETURN and self.creation_mode:
                    if not self.delete_mode:
                        self._create_and_save_interactable()
                    else:
                        self.ui_manager.show_message("Cannot create in delete mode - use TAB to switch modes", 2000)

        return True
    
    def handle_resize(self, width: int, height: int):
        """Handle window resize events"""
        # Update screen dimensions
        self.screen_width = width
        self.screen_height = height
        
        # Only update windowed_size if we're actually in windowed mode
        if not self.is_fullscreen:
            self.windowed_size = (width, height)
        
        # Update screen surface
        if not self.is_fullscreen:
            self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        
        # Reinitialize UI components that depend on screen size
        if hasattr(self.ui_manager, 'dialogue_box'):
            self.ui_manager.dialogue_box._init_dimensions()
        
        if hasattr(self.ui_manager, 'password_ui'):
            self.ui_manager.password_ui._init_dimensions()
        
        # Update camera viewport
        if hasattr(self.level_manager, 'camera'):
            self.level_manager.camera.update_viewport(width, height)
        
        # Show popup notification
        self.ui_manager.show_popup(f"Window resized to {width}x{height}")

    def _update_mouse_tile_coords(self):
        """Update mouse tile coordinates based on current mouse position"""
        if not self.level_manager.current_level:
            self.mouse_tile_x = 0
            self.mouse_tile_y = 0
            return
        
        try:
            # Convert screen coordinates to world coordinates
            camera = self.level_manager.camera
            world_x = (self.mouse_x / camera.zoom) + camera.x
            world_y = (self.mouse_y / camera.zoom) + camera.y
            
            # Convert world coordinates to tile coordinates
            self.mouse_tile_x = int(world_x // 16)
            self.mouse_tile_y = int(world_y // 16)
        except (ZeroDivisionError, AttributeError) as e:
            # Fallback to safe values if there's an error
            self.mouse_tile_x = 0
            self.mouse_tile_y = 0
            print(f"Error updating mouse coordinates: {e}")
    
    def _handle_mouse_click(self, pos):
        """Handle mouse click events"""
        # Don't handle mouse clicks when paused
        if self.paused:
            return
            
        # Safety check - make sure we have valid coordinates
        if not hasattr(self, 'mouse_tile_x') or not hasattr(self, 'mouse_tile_y'):
            self._update_mouse_tile_coords()
        
        # Additional safety check for level
        if not self.level_manager.current_level:
            return
        
        if self.creation_mode:
            if self.delete_mode:
                # Delete interactable at clicked position
                success = interactable_manager.delete_interactable_at_position(
                    self.mouse_tile_x, self.mouse_tile_y
                )
                if success:
                    # Reload the level to show the changes
                    current_name = self.level_manager.current_level_name
                    if current_name:
                        self.level_manager.load_level(current_name)
                        self.load_level_interactables()
                    self.ui_manager.show_message(f"Deleted interactable at ({self.mouse_tile_x}, {self.mouse_tile_y})", 2000)
                else:
                    self.ui_manager.show_message("No interactable found at this position", 1500)
            else:
                # Add/remove tile from selection
                tile_coord = (self.mouse_tile_x, self.mouse_tile_y)
                if tile_coord in self.selected_tiles:
                    self.selected_tiles.remove(tile_coord)
                else:
                    self.selected_tiles.add(tile_coord)
        else:
            # Try to interact with clicked tile
            try:
                player_x, player_y = self.player.get_position()

                result = interactable_manager.interact_at(
                    self.mouse_tile_x, self.mouse_tile_y, 
                    player_x, player_y
                )
                if result.get("type") != "none":
                    self.handle_interaction(result)
            except Exception as e:
                print(f"Error during interaction: {e}")
                self.ui_manager.show_message("Error during interaction", 2000)
    
    def _create_and_save_interactable(self):
        """Create interactable from selected tiles and save permanently to JSON"""
        if not self.selected_tiles:
            self.ui_manager.show_message("No tiles selected!", 2000)
            return
        
        if self.creation_type == "door":
            # Create door(s) - each selected tile becomes a separate door
            success_count = 0
            for tile_x, tile_y in self.selected_tiles:
                # Don't specify required_rules - let the system use level's rule_count
                success = interactable_manager.save_door_to_level_file(
                    tile_x, tile_y  # Remove the hardcoded required_rules=3
                )
                if success:
                    success_count += 1
            
            if success_count > 0:
                # Force reload the level from file to show the new doors
                current_name = self.level_manager.current_level_name
                if current_name:
                    # Reload from file, not memory
                    if self.level_manager.load_level(current_name):
                        self.load_level_interactables()
                        print(f"Successfully reloaded level '{current_name}' from file to show new doors")
                    else:
                        print(f"Failed to reload level '{current_name}' from file")
                
                self.ui_manager.show_message(
                    f"Created {success_count} door(s)!", 3000
                )
            else:
                self.ui_manager.show_message("Failed to create doors!", 2000)
        else:
            # Create note interactables (existing functionality)
            success = interactable_manager.save_interactables_to_level_file(
                self.selected_tiles.copy(), 
                tile_id="25"
            )
            
            if success:
                # Force reload the level from file to show the new interactables
                current_name = self.level_manager.current_level_name
                if current_name:
                    # Reload from file, not memory
                    if self.level_manager.load_level(current_name):
                        self.load_level_interactables()
                        print(f"Successfully reloaded level '{current_name}' from file to show new interactables")
                    else:
                        print(f"Failed to reload level '{current_name}' from file")
                
                self.ui_manager.show_message(
                    f"Saved {len(self.selected_tiles)} tiles as permanent interactables!", 3000
                )
            else:
                self.ui_manager.show_message("Failed to save interactables!", 2000)
        
        # Clear selection
        self.selected_tiles.clear()
    
    def _toggle_layer(self, layer_name: str):
        """Toggle visibility of a specific layer (demo feature)"""
        # This is a simple implementation - you'd want to track layer states properly
        print(f"Layer toggle for '{layer_name}' - implement layer visibility tracking as needed")
    
    def _find_doors_in_level(self) -> List[Tuple[int, int]]:
        """Find all door positions in the current level"""
        doors = []
        for obj in interactable_manager.interactables:
            if obj.__class__.__name__ == 'Door':
                doors.append((obj.x, obj.y))
        return doors
    
    def _get_nearest_door_position(self) -> Tuple[int, int]:
        """Get the position of the nearest door to the player"""
        doors = self._find_doors_in_level()
        if not doors:
            return None
        
        player_x, player_y = self.player.get_position()
        
        player_tile_x = int(player_x // 16)
        player_tile_y = int(player_y // 16)
        
        # Find the nearest door
        nearest_door = None
        nearest_distance = float('inf')
        
        for door_x, door_y in doors:
            # Calculate distance to door
            dx = door_x - player_tile_x
            dy = door_y - player_tile_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_door = (door_x, door_y)
        
        return nearest_door
    
    def _calculate_direction_to_door(self, door_pos: Tuple[int, int]) -> float:
        """Calculate the angle (in radians) from player to door"""
        if not door_pos:
            return 0
        
        player_x, player_y = self.player.get_position()
        
        player_tile_x = int(player_x // 16)
        player_tile_y = int(player_y // 16)
        
        door_x, door_y = door_pos
        
        # Calculate direction vector
        dx = door_x - player_tile_x
        dy = door_y - player_tile_y
        
        # Calculate angle (atan2 returns angle in radians)
        # Note: In pygame, Y axis is flipped (positive Y goes down)
        angle = math.atan2(dy, dx)
        
        return angle
            
    def update(self):
        """Update game state"""
        if self.paused or self.ui_manager.password_ui.visible or self.ui_manager.dialogue_box.is_active:
            self.ui_manager.update(self.clock.get_time() / 1000.0)
            return
        
        # Handle player movement
        keys = pygame.key.get_pressed()
        self.player.move(keys, self.level_manager)
        
        # Update camera to follow player
        player_x, player_y = self.player.get_position()
        self.level_manager.update_camera(
            player_x, player_y,
            smooth=self.smooth_camera
        )

        self.ui_manager.compass.update_position()
        
        # Update UI manager
        self.ui_manager.update(self.clock.get_time() / 1000.0)
        
        # Check for nearby interactables
        self.check_nearby_interactables()
    
    def render(self):
        """Render the game"""
        # Fill screen with black background
        self.screen.fill((0, 0, 0))
        
        # Render level with layered sprites
        self.level_manager.render_level(debug_info=self.show_debug)

        self._draw_proximity_hints()
        if self.show_coordinates:
            self._draw_existing_interactables()

        game_data = {
            'player_speed': self.player.speed,
            'camera_zoom': self.level_manager.camera.zoom,
            'nearest_door': self._get_nearest_door_position(),
            'door_angle': self._calculate_direction_to_door(self._get_nearest_door_position()),
            'current_rules': self.current_level_rules,
            'total_rules': (
                interactable_manager.level_metadata.get("rule_count", 0) 
                if hasattr(interactable_manager, 'level_metadata') 
                else len(self.current_level_rules)
            ),
            'paused': self.paused,
            'player_pos': self.player.get_position(),
            'mouse_pos': (self.mouse_x, self.mouse_y),
            'fps': self.clock.get_fps(),
            'debug_info': {
                'mouse_tile': (self.mouse_tile_x, self.mouse_tile_y),
                'creation_mode': self.creation_mode,
                'creation_type': self.creation_type,
                'selected_tiles': self.selected_tiles
            }
        }

        if self.creation_mode:
            self._draw_selected_tiles()

        # Render player
        self.player.render(self.screen, self.level_manager.camera)

        # Draw pause effect before UI so PAUSED text appears on top
        if self.paused:
            # Dimming overlay
            dim_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            dim_surface.fill((0, 0, 0, 150))  # Semi-transparent black
            self.screen.blit(dim_surface, (0, 0))

            # Static effect
            for _ in range(2000): # Draw 2000 static particles
                x = random.randint(0, self.screen_width)
                y = random.randint(0, self.screen_height)
                color = random.choice([(200, 200, 200), (150, 150, 150), (100,100,100)]) # Shades of gray
                self.screen.set_at((x,y), color)

        # Render UI (including PAUSED text)
        self.ui_manager.render(game_data)

        # Update display
        pygame.display.flip()
    
    def _draw_selected_tiles(self):
        """Draw overlay for selected tiles in creation mode"""
        zoom = self.level_manager.camera.zoom
        camera = self.level_manager.camera
        
        for tile_x, tile_y in self.selected_tiles:
            # Convert tile coordinates to screen coordinates
            world_x = tile_x * 16
            world_y = tile_y * 16
            screen_x, screen_y = camera.apply(world_x, world_y)
            
            # Draw selection overlay
            rect = pygame.Rect(
                int(screen_x * zoom), 
                int(screen_y * zoom), 
                int(16 * zoom), 
                int(16 * zoom)
            )
            pygame.draw.rect(self.screen, (255, 255, 0, 128), rect, 2)  # Yellow border
    
    def _draw_coordinate_debug(self):
        """Draw coordinate debug information"""
        try:
            font = pygame.font.Font(None, 24)
            small_font = pygame.font.Font(None, 18)

            player_x, player_y = self.player.get_position()
            
            # Player coordinates
            player_tile_x = int(player_x // 16)
            player_tile_y = int(player_y // 16)
            
            debug_info = [
                f"Player: ({player_tile_x}, {player_tile_y}) | Pixel: ({int(self.player.get_position()[0])}, {int(player_y)})",
                f"Mouse: ({self.mouse_tile_x}, {self.mouse_tile_y}) | Screen: ({self.mouse_x}, {self.mouse_y})",
            ]
            
            # Get tile ID information at mouse position
            try:
                mouse_world_x = self.mouse_tile_x * 16
                mouse_world_y = self.mouse_tile_y * 16
                sprites_at_mouse = self.level_manager.get_sprites_at_position(mouse_world_x, mouse_world_y)
                
                if sprites_at_mouse:
                    # Show tile IDs for all sprites at this position (from background to foreground)
                    tile_ids = []
                    for sprite in sprites_at_mouse:
                        if hasattr(sprite, 'tile_data') and 'id' in sprite.tile_data:
                            tile_id = sprite.tile_data['id']
                            layer_depth = sprite.layer_depth
                            tile_ids.append(f"ID:{tile_id}(L{layer_depth})")
                    
                    if tile_ids:
                        debug_info.append(f"Tile IDs: {', '.join(tile_ids)}")
                    else:
                        debug_info.append("Tile IDs: No sprites with IDs")
                else:
                    debug_info.append("Tile IDs: No sprites at position")
            except Exception as e:
                debug_info.append(f"Tile IDs: Error getting sprite info")
            
            # Check if mouse is over an interactable (with safety check)
            try:
                mouse_interactable = interactable_manager.get_interactable_at(self.mouse_tile_x, self.mouse_tile_y)
                if mouse_interactable:
                    if hasattr(mouse_interactable, 'tiles'):
                        debug_info.append(f"Mouse over: Multi-tile {mouse_interactable.__class__.__name__} ({len(mouse_interactable.tiles)} tiles)")
                    else:
                        debug_info.append(f"Mouse over: {mouse_interactable.__class__.__name__}")
            except Exception as e:
                debug_info.append(f"Mouse over: Error checking interactable")
            
            if self.creation_mode:
                debug_info.append(f"Selected tiles: {len(self.selected_tiles)}")
                mode_text = "DELETE" if self.delete_mode else self.creation_type.upper()
                debug_info.append(f"Creation mode: {mode_text}")
                if self.selected_tiles and not self.delete_mode:
                    # Show how many groups the selection would create
                    try:
                        if self.creation_type == "door":
                            debug_info.append(f"Would create {len(self.selected_tiles)} door(s)")
                        else:
                            groups = self._group_adjacent_tiles(self.selected_tiles)
                            debug_info.append(f"Would create {len(groups)} interactable(s)")
                    except:
                        debug_info.append(f"Would create interactable(s)")
                    debug_info.append(f"Selection: {list(self.selected_tiles)[:3]}{'...' if len(self.selected_tiles) > 3 else ''}")
                elif self.delete_mode:
                    debug_info.append("Click on interactables to delete them")
            
            y_offset = 60  # Start below zoom indicator
            for text in debug_info:
                # Render with outline for visibility
                text_surface = font.render(text, True, (255, 255, 255))
                outline_surface = font.render(text, True, (0, 0, 0))
                
                self.screen.blit(outline_surface, (11, y_offset + 1))
                self.screen.blit(text_surface, (10, y_offset))
                y_offset += 25
            
            # Add color legend
            y_offset += 10
            legend_title = font.render("Interactable Colors:", True, (255, 255, 255))
            legend_title_outline = font.render("Interactable Colors:", True, (0, 0, 0))
            self.screen.blit(legend_title_outline, (11, y_offset + 1))
            self.screen.blit(legend_title, (10, y_offset))
            y_offset += 25
            
            # Color legend entries
            legend_entries = [
                ((0, 255, 0), "Green: Notes with rules"),
                ((150, 150, 150), "Light Gray: Empty interactables"),
                ((100, 100, 100), "Dark Gray: Collected/claimed"),
                ((255, 0, 255), "Magenta: Locked doors"),
                ((0, 255, 255), "Cyan: Open doors"),
                ((255, 255, 0), "Yellow: Selected tiles / Proximity hint"),
                ((255, 255, 255), "White corner: Multi-tile group")
            ]
            
            for color, description in legend_entries:
                # Draw color box
                color_rect = pygame.Rect(10, y_offset, 12, 12)
                pygame.draw.rect(self.screen, color, color_rect)
                pygame.draw.rect(self.screen, (0, 0, 0), color_rect, 1)
                
                # Draw description
                text_surface = small_font.render(description, True, (255, 255, 255))
                outline_surface = small_font.render(description, True, (0, 0, 0))
                self.screen.blit(outline_surface, (26, y_offset - 1))
                self.screen.blit(text_surface, (25, y_offset - 2))
                y_offset += 18
                
        except Exception as e:
            # Fallback if there's any error in debug display
            print(f"Error in coordinate debug display: {e}")
    
    def _group_adjacent_tiles(self, tiles: Set[Tuple[int, int]]) -> List[Set[Tuple[int, int]]]:
        """Group adjacent tiles together (for preview in debug display)"""
        if not tiles:
            return []
        
        remaining_tiles = tiles.copy()
        groups = []
        
        while remaining_tiles:
            # Start a new group with any remaining tile
            current_group = set()
            to_process = [remaining_tiles.pop()]
            
            while to_process:
                current_tile = to_process.pop()
                if current_tile in current_group:
                    continue
                
                current_group.add(current_tile)
                x, y = current_tile
                
                # Check all 4 adjacent positions (not diagonal)
                adjacent_positions = [
                    (x - 1, y),  # Left
                    (x + 1, y),  # Right
                    (x, y - 1),  # Up
                    (x, y + 1),  # Down
                ]
                
                for adj_pos in adjacent_positions:
                    if adj_pos in remaining_tiles:
                        to_process.append(adj_pos)
                        remaining_tiles.remove(adj_pos)
            
            groups.append(current_group)
        
        return groups
    
    def load_level_interactables(self):
        """Load interactables for the current level"""
        if self.level_manager.current_level:
            # Reset current level rules when loading a new level
            self.current_level_rules = []
            
            # Only clear game state rules if we're not transitioning from another level
            if not self.is_transitioning:
                game_state.clear_rules_for_testing()
            
            # Set the current level path for saving
            level_path = self.level_manager.get_current_level_path()
            if level_path:
                interactable_manager.set_current_level_path(level_path)
            
            # Pass the used rules to avoid selecting previously used rules
            interactable_manager.load_from_level_data(self.level_manager.current_level.raw_data, self.used_rules)
            
            # Track newly selected rules as used
            current_level_rules = interactable_manager.get_current_level_rules()
            for rule in current_level_rules:
                self.used_rules.add(rule)
            
            print(f"Total rules used across all levels: {len(self.used_rules)}")
            
            # Update door requirements based on accumulated rules
            self._update_door_requirements()
            
            # Reset transition flag after loading
            self.is_transitioning = False
    
    def check_nearby_interactables(self):
        """Check for nearby interactables and show interaction hints"""
        player_x, player_y = self.player.get_position()

        # Convert player position to tile coordinates
        player_tile_x = int(player_x // 16)
        player_tile_y = int(player_y // 16)
        
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
        player_x, player_y = self.player.get_position()
        player_tile_x, player_tile_y = self.player.get_tile_position()
        
        # Check adjacent tiles for interactables
        adjacent_positions = [
            (player_tile_x, player_tile_y),      # Current tile
            (player_tile_x - 1, player_tile_y),  # Left
            (player_tile_x + 1, player_tile_y),  # Right
            (player_tile_x, player_tile_y - 1),  # Up
            (player_tile_x, player_tile_y + 1),  # Down
        ]
        
        for tile_x, tile_y in adjacent_positions:
            result = interactable_manager.interact_at(tile_x, tile_y, player_x, player_y)
            if result.get("type") != "none":
                self.handle_interaction(result)
                break
    
    def handle_interaction(self, result: Dict[str, Any]):
        """Handle interaction results"""
        interaction_type = result.get("type", "none")
        message = result.get("message", "")
        
        # Play appropriate sound effect based on interaction type and message content
        if interaction_type == "note_collected":
            if ':' in message and "You found a rule:" not in message:  # NPC interaction
                self.npc_sfx.play()
            else:  # Regular note/object interaction
                self.interact_sfx.play()
        elif interaction_type != "none":  # Other valid interactions
            self.interact_sfx.play()

        # Handle different types of interactions
        if interaction_type == "note_collected":
            rule = result.get("rule", "")
            if rule:
                game_state.add_rule(rule, result.get("note_id"))
                # Add to current level rules
                if rule not in self.current_level_rules:
                    self.current_level_rules.append(rule)
                
                # Show appropriate message
                if message and "Rule collected:" not in message:  # NPC message
                    self.ui_manager.show_message(message, 3000)
                else:  # Default rule collection message
                    self.ui_manager.show_message(f"Rule collected: {rule}", 3000)
                
        elif interaction_type == "note_already_collected":
            if ':' in message and "Rule collected:" not in message:  # NPC repeated interaction
                self.ui_manager.show_message(message, 2000)
            else:  # Default already collected message
                self.ui_manager.show_message("Already read this note.", 2000)
                
        elif interaction_type == "empty_interactable":
            if ':' in message and "Rule collected:" not in message:  # NPC without rule
                self.ui_manager.show_message(message, 2000)
            else:  # Default empty message
                self.ui_manager.show_message("There's nothing here.", 2000)
                
        elif interaction_type == "door_locked":
            self.click_sfx.play()
            self.ui_manager.show_message(message or "Door is locked.", 3000)
                
        elif interaction_type == "door_password_prompt":
            # Show password UI with preserved password if available
            self.click_sfx.play()
            rules = result.get("rules", [])
            collected_rules = result.get("collected_rules", [])
            door = result.get("door")
            
            # Combine accumulated rules from previous levels with current level collected rules
            combined_collected_rules = self.accumulated_rules.copy()
            for rule in collected_rules:
                if rule not in combined_collected_rules:
                    combined_collected_rules.append(rule)
            
            self.ui_manager.show(
                rules, 
                door, 
                self.handle_password_result, 
                combined_collected_rules, 
                self.last_successful_password, 
                self.handle_password_ui_close
            )
                
        elif interaction_type == "door_open":
            self.ui_manager.show_message(message or "Door is open.", 2000)
                
        elif interaction_type == "level_transition":
            # Handle level transition
            next_level = result.get("next_level")
            self.ui_manager.show_message(message or f"Entering {next_level}...", 2000)
            
            if next_level:
                self.transition_to_level(next_level)
    
    def handle_password_result(self, result: Dict[str, Any]):
        """Handle password attempt results"""
        self.click_sfx.play()
        print(f"DEBUG: Password result received: {result}")
        
        if result.get("success", False):
            self.success_sfx.play() 
            print(f"DEBUG: Password was successful!")
            
            # Check if we just completed level-4 - if so, trigger game completion
            # This should happen for any successful password in level-4, regardless of result type
            current_level = self.level_manager.current_level_name
            print(f"DEBUG: Current level: '{current_level}', Result type: '{result.get('type')}'")
            
            if current_level == "level-4":
                print("Level-4 completed! Triggering game completion...")
                self.ui_manager.show_popup("Congratulations! You have completed the game!", 3000)
                
                # Set a flag to exit the game after a brief delay
                pygame.time.set_timer(pygame.USEREVENT + 1, 3000)  # Exit after 3 seconds
                self.ui_manager.password_ui.hide()
                return
            
            # Handle level transitions for other levels
            if result.get("type") == "level_transition":
                print(f"DEBUG: Result type is level_transition")
                next_level = result.get("next_level")
                
                # Store successful password
                if self.ui_manager.password_ui.password_input:
                    self.last_successful_password = self.ui_manager.password_ui.password_input.text
                
                # Accumulate rules
                current_level_rules = self.current_level_rules if self.current_level_rules else []
                for rule in current_level_rules:
                    if rule != "????" and rule not in self.accumulated_rules:
                        self.accumulated_rules.append(rule)
                        print(f"Accumulated rule: {rule}")
                
                # Extract current level number from level name for display
                level_num = ''.join(filter(str.isdigit, current_level))
                next_num = str(int(level_num) + 1) if level_num else ""
                
                # Show popup notification for level transition
                self.ui_manager.show_popup(f"Your password was accepted! Commencing Level {next_num}...", 5000)
                
                self.is_transitioning = True
                
                if next_level:
                    self.transition_to_level(next_level)

                self.ui_manager.password_ui.hide()
            else:
                print(f"DEBUG: Result type is not level_transition, it's: {result.get('type')}")
                # For non-transition results (like door_opened), just hide the UI
                self.ui_manager.password_ui.hide()
        else:
            self.invalid_sfx.play()
            print(f"DEBUG: Password was not successful")
            # Show error as popup instead of message
            message = result.get("message", "Your password is invalid.")
            self.ui_manager.show_popup(message, 2000)
    
    def _draw_existing_interactables(self):
        """Draw outlines around existing interactable tiles (debug only)"""
        zoom = self.level_manager.camera.zoom
        camera = self.level_manager.camera
        
        for obj in interactable_manager.interactables:
            if hasattr(obj, 'tiles'):  # Multi-tile interactable
                # Draw outline around all tiles in the group
                for tile_x, tile_y in obj.tiles:
                    world_x = tile_x * 16
                    world_y = tile_y * 16
                    screen_x, screen_y = camera.apply(world_x, world_y)
                    
                    rect = pygame.Rect(
                        int(screen_x * zoom), 
                        int(screen_y * zoom), 
                        int(16 * zoom), 
                        int(16 * zoom)
                    )
                    
                    # Determine color based on interactable type and state
                    color = self._get_interactable_color(obj)
                    
                    # Draw thicker outline for multi-tile groups
                    pygame.draw.rect(self.screen, color, rect, 3)
                    
                    # Add a small indicator in the corner for multi-tile groups
                    corner_size = max(4, int(4 * zoom))
                    corner_rect = pygame.Rect(
                        rect.right - corner_size, 
                        rect.top, 
                        corner_size, 
                        corner_size
                    )
                    pygame.draw.rect(self.screen, (255, 255, 255), corner_rect)
                    
            else:  # Single-tile interactable
                world_x = obj.x * 16
                world_y = obj.y * 16
                screen_x, screen_y = camera.apply(world_x, world_y)
                
                rect = pygame.Rect(
                    int(screen_x * zoom), 
                    int(screen_y * zoom), 
                    int(16 * zoom), 
                    int(16 * zoom)
                )
                
                # Determine color based on interactable type and state
                color = self._get_interactable_color(obj)
                
                # Draw outline
                pygame.draw.rect(self.screen, color, rect, 2)
    
    def _get_interactable_color(self, obj) -> tuple:
        """Get the appropriate color for an interactable based on its type and state"""
        # Check if it's collected/claimed
        if hasattr(obj, 'collected') and obj.collected:
            return (100, 100, 100)  # Gray for collected/claimed
        
        # Check if it's an open door
        if hasattr(obj, 'is_open') and obj.is_open:
            return (0, 255, 255)  # Cyan for open doors
        
        # Check object type
        if obj.__class__.__name__ == 'Door':
            return (255, 0, 255)  # Magenta for locked doors
        elif obj.__class__.__name__ == 'EmptyInteractable':
            return (150, 150, 150)  # Light gray for empty interactables
        elif obj.__class__.__name__ == 'MultiTileEmptyInteractable':
            return (150, 150, 150)  # Light gray for multi-tile empty interactables
        elif obj.__class__.__name__ == 'Note':
            return (0, 255, 0)  # Green for notes with rules
        elif obj.__class__.__name__ == 'MultiTileNote':
            return (0, 255, 0)  # Green for multi-tile notes with rules
        else:
            return (255, 255, 0)  # Yellow for unknown/other types
    
    def _show_interactables_info(self):
        """Show information about programmatic interactables for the current level"""
        if not self.level_manager.current_level:
            self.ui_manager.show_message("No level loaded!", 2000)
            return
        
        level_name = self.level_manager.current_level_name or "unknown"
        programmatic = interactable_manager.list_programmatic_interactables(level_name)
        
        if level_name in programmatic and programmatic[level_name]:
            count = len(programmatic[level_name])
            self.ui_manager.show_message(f"Level '{level_name}' has {count} programmatic interactables", 3000)
            
            # Print detailed info to console
            print(f"\n=== Programmatic Interactables for '{level_name}' ===")
            for i, interactable in enumerate(programmatic[level_name]):
                print(f"{i+1}. Type: {interactable['type']}")
                print(f"   Coordinates: {interactable['coordinates']}")
                if 'rule' in interactable:
                    print(f"   Rule: {interactable['rule']}")
                if 'required_rules' in interactable:
                    print(f"   Required Rules: {interactable['required_rules']}")
                print()
        else:
            self.ui_manager.show_message(f"No programmatic interactables for '{level_name}'", 2000)
    
    def _copy_mouse_coordinates(self):
        """Print current mouse coordinates in a format ready for code"""
        try:
            # Safety check for coordinates
            if not hasattr(self, 'mouse_tile_x') or not hasattr(self, 'mouse_tile_y'):
                self._update_mouse_tile_coords()
            
            level_name = self.level_manager.current_level_name or "unknown"
            
            # Print single tile format
            print(f"\n=== Mouse Coordinates ===")
            print(f"Level: {level_name}")
            print(f"Tile Coordinates: ({self.mouse_tile_x}, {self.mouse_tile_y})")
            print(f"\n--- Code Examples ---")
            print(f"# Single tile interactable:")
            print(f'interactable_manager.add_single_tile_interactable(')
            print(f'    "{level_name}", {self.mouse_tile_x}, {self.mouse_tile_y},')
            print(f'    "Your rule text here"')
            print(f')')
            print(f"\n# Door:")
            print(f'interactable_manager.add_door_coordinates(')
            print(f'    "{level_name}", {self.mouse_tile_x}, {self.mouse_tile_y},')
            print(f'    required_rules=4')
            print(f')')
            print(f"\n# Multi-tile (add more coordinates):")
            print(f'interactable_manager.add_multi_tile_interactable_coords(')
            print(f'    "{level_name}",')
            print(f'    [({self.mouse_tile_x}, {self.mouse_tile_y}), (x2, y2), (x3, y3)],')
            print(f'    "Your multi-tile rule text here"')
            print(f')')
            
            self.ui_manager.show_message(f"Coordinates ({self.mouse_tile_x}, {self.mouse_tile_y}) printed to console!", 2000)
        except Exception as e:
            print(f"Error copying mouse coordinates: {e}")
            self.ui_manager.show_message("Error copying coordinates", 2000)
    
    def _clean_duplicate_interactables(self):
        """Clean up duplicate interactables"""
        success = interactable_manager.clean_duplicate_interactables()
        
        if success:
            # Reload the level to show the cleaned up interactables
            current_name = self.level_manager.current_level_name
            if current_name:
                self.level_manager.load_level(current_name)
                self.load_level_interactables()
            
            self.ui_manager.show_message("Duplicate interactables cleaned up!", 3000)
        else:
            self.ui_manager.show_message("Failed to clean up duplicates!", 2000)
    
    def transition_to_level(self, level_name: str):
        """Transition to a new level"""
        try:
            if self.level_manager.load_level(level_name):
                # Reset player position to the new level's starting point
                start_x, start_y = self.level_manager.get_level_starting_point()
                self.player.set_position(start_x, start_y)
                
                # Set transition flag and load interactables
                self.is_transitioning = True
                self.load_level_interactables()
                return True
        except Exception as e:
            print(f"Error transitioning to level {level_name}: {e}")
        return False
    
    def _update_door_requirements(self):
        """Update door required rules based on accumulated rules plus current level rules"""
        if not self.level_manager.current_level:
            return
        
        # Get current level's rule count
        current_level_rule_count = 0
        if hasattr(interactable_manager, 'level_metadata') and interactable_manager.level_metadata:
            current_level_rule_count = interactable_manager.level_metadata.get("rule_count", 0)
        
        # Calculate total required rules (accumulated + current level)
        total_required_rules = len(self.accumulated_rules) + current_level_rule_count
        
        # Update all doors in the current level
        for obj in interactable_manager.interactables:
            if obj.__class__.__name__ == 'Door':
                obj.set_required_rules(total_required_rules)
                print(f"Updated door at ({obj.x}, {obj.y}) to require {total_required_rules} rules")
        
        print(f"Door requirements updated: {len(self.accumulated_rules)} accumulated + {current_level_rule_count} current = {total_required_rules} total")
    
    def _draw_proximity_hints(self):
        """Draw transparent pale yellow border glow for nearby interactables"""
        zoom = self.level_manager.camera.zoom
        camera = self.level_manager.camera

        player_x, player_y = self.player.get_position()
        
        # Convert player position to tile coordinates for proper comparison
        player_tile_x = int(player_x // 16)
        player_tile_y = int(player_y // 16)
        
        # Collect all nearby interactables (both single and multi-tile)
        nearby_interactables = []
        
        for obj in interactable_manager.interactables:
            # Check if player is adjacent to this interactable
            is_player_nearby = False
            
            if hasattr(obj, 'tiles'):  # Multi-tile interactable
                # Check if any tile in the group is adjacent to player
                for tile_x, tile_y in obj.tiles:
                    dx = abs(tile_x - player_tile_x)
                    dy = abs(tile_y - player_tile_y)
                    # Adjacent means 1 tile away (including diagonals)
                    if dx <= 1 and dy <= 1:
                        is_player_nearby = True
                        break
            else:  # Single-tile interactable
                dx = abs(obj.x - player_tile_x)
                dy = abs(obj.y - player_tile_y)
                # Adjacent means 1 tile away (including diagonals)
                if dx <= 1 and dy <= 1:
                    is_player_nearby = True
            
            if is_player_nearby:
                nearby_interactables.append(obj)
        
        # Group all adjacent interactables and their tiles
        grouped_tiles = self._group_all_adjacent_interactables(nearby_interactables)
        
        # Draw unified highlights for each group of adjacent interactables
        for tile_group in grouped_tiles:
            # Determine the color for this group
            group_color = self._determine_group_color_for_all(tile_group, nearby_interactables)
            self._draw_unified_highlight(tile_group, camera, zoom, group_color)
    
    def _group_all_adjacent_interactables(self, nearby_interactables):
        """Group all adjacent interactables together (both single-tile and multi-tile)"""
        if not nearby_interactables:
            return []
        
        # Collect all tiles from all interactables
        all_tiles = set()
        for obj in nearby_interactables:
            if hasattr(obj, 'tiles'):  # Multi-tile interactable
                for tile_x, tile_y in obj.tiles:
                    all_tiles.add((tile_x, tile_y))
            else:  # Single-tile interactable
                all_tiles.add((obj.x, obj.y))
        
        # Group adjacent tiles together
        grouped_tiles = []
        remaining_tiles = all_tiles.copy()
        
        while remaining_tiles:
            # Start a new group with any remaining tile
            current_group = set()
            to_process = [remaining_tiles.pop()]
            
            while to_process:
                current_tile = to_process.pop()
                if current_tile in current_group:
                    continue
                
                current_group.add(current_tile)
                x, y = current_tile
                
                # Check all 4 adjacent positions (not diagonal)
                adjacent_positions = [
                    (x - 1, y),  # Left
                    (x + 1, y),  # Right
                    (x, y - 1),  # Up
                    (x, y + 1),  # Down
                ]
                
                for adj_pos in adjacent_positions:
                    if adj_pos in remaining_tiles:
                        to_process.append(adj_pos)
                        remaining_tiles.remove(adj_pos)
            
            grouped_tiles.append(current_group)
        
        return grouped_tiles
    
    def _determine_group_color_for_all(self, tile_group, nearby_interactables):
        """Determine the appropriate color for a group of tiles (including single-tile interactables)"""
        # Check what types of interactables are in this group
        has_collected_or_used = False
        
        for obj in nearby_interactables:
            # Check if this object's tiles are in the current group
            obj_tiles_in_group = False
            
            if hasattr(obj, 'tiles'):  # Multi-tile interactable
                obj_tiles_in_group = any((tile_x, tile_y) in tile_group for tile_x, tile_y in obj.tiles)
            else:  # Single-tile interactable
                obj_tiles_in_group = (obj.x, obj.y) in tile_group
            
            if obj_tiles_in_group:
                if (hasattr(obj, 'collected') and obj.collected) or (hasattr(obj, 'is_open') and obj.is_open):
                    has_collected_or_used = True
                    break  # Found a collected/used item, no need to check further
        
        # For proximity hints: only grey for collected/used, yellow for everything else
        if has_collected_or_used:
            return (180, 180, 180, 180)  # Grey for collected/used items
        else:
            return (255, 255, 50, 180)   # Yellow for all active/unused interactables
    
    def _draw_unified_highlight(self, tiles: set, camera, zoom: float, border_color: tuple):
        """Draw a unified highlight around a group of tiles"""
        if not tiles:
            return
        
        border_thickness = 2
        tile_size = int(16 * zoom)
        
        # For each tile, draw a filled background and only external borders
        for tile_x, tile_y in tiles:
            world_x = tile_x * 16
            world_y = tile_y * 16
            screen_x, screen_y = camera.apply(world_x, world_y)
            
            tile_rect = pygame.Rect(
                int(screen_x * zoom), 
                int(screen_y * zoom), 
                tile_size, 
                tile_size
            )
            
            # Create a surface for this tile with alpha support
            tile_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
            
            # Fill with a semi-transparent background color
            background_color = (*border_color[:3], 40)  # Much more transparent background
            tile_surface.fill(background_color)
            
            # Check which edges should have borders (only if adjacent tile is not in the group)
            
            # Top edge
            if (tile_x, tile_y - 1) not in tiles:
                pygame.draw.rect(tile_surface, border_color, 
                               (0, 0, tile_size, border_thickness))
            
            # Bottom edge
            if (tile_x, tile_y + 1) not in tiles:
                pygame.draw.rect(tile_surface, border_color, 
                               (0, tile_size - border_thickness, tile_size, border_thickness))
            
            # Left edge
            if (tile_x - 1, tile_y) not in tiles:
                pygame.draw.rect(tile_surface, border_color, 
                               (0, 0, border_thickness, tile_size))
            
            # Right edge
            if (tile_x + 1, tile_y) not in tiles:
                pygame.draw.rect(tile_surface, border_color, 
                               (tile_size - border_thickness, 0, border_thickness, tile_size))
            
            # Blit the tile surface to screen
            self.screen.blit(tile_surface, tile_rect)
    
    def handle_password_ui_close(self, password: str):
        """Handle password UI being closed via X button - save the current password"""
        self.click_sfx.play()
        if password:
            self.last_successful_password = password
            print(f"Password saved when closing UI: {password}")
    
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
        
        # Don't call pygame.quit() or sys.exit() - let control return to main.py
        print("DEBUG: GameDemo.run() exiting normally, returning control to main.py")

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
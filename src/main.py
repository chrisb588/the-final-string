import pygame
import sys
import math
from typing import Dict, Any, Set, Tuple, List
from levels.manager import LayeredLevelManager
from game_state import game_state
from entities.interactables import interactable_manager
from ui.password_ui import PasswordUI, MessageUI, RulesDisplayUI
from ui.matrix_background import MatrixBackground
from interactable_config import setup_level_interactables
from entities.player import Player

class GameDemo:
    """Demo showing the layered tileset renderer in action"""
    
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        
        # Screen settings
        self.screen_width = 1024
        self.screen_height = 768
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Layered Tileset Demo")
        
        # Game settings
        self.fps = 60
        self.clock = pygame.time.Clock()

        # Debug and control flags
        self.show_debug = False
        self.smooth_camera = True
        self.paused = False
        self.show_speed_debug = False
        
        # Mouse tracking for debug coordinates
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_tile_x = 0
        self.mouse_tile_y = 0
        self.show_coordinates = False
        
        # Interactable creation mode
        self.creation_mode = False
        self.selected_tiles = set()  # Store selected tile coordinates
        self.creation_type = "note"  # "note" or "door" - what type to create
        self.delete_mode = False  # Whether we're in delete mode
        
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
        if self.level_manager.load_first_level():
            start_x, start_y = self.level_manager.get_level_starting_point()
            self.player.set_position(start_x, start_y)
            self.load_level_interactables()
        else:
            print("No levels found! Make sure your level files are in the correct directory.")
        
        # UI components - Pass self (PasswordUI) to other UI elements for consistent styling
        self.password_ui = PasswordUI(self.screen)
        self.message_ui = MessageUI(self.screen, ui_manager=self.password_ui)
        self.rules_ui = RulesDisplayUI(self.screen, ui_manager=self.password_ui)
        
        # Matrix background
        self.matrix_background = MatrixBackground(
            self.screen_width, 
            self.screen_height, 
            gif_path="assets/images/matrix_background.gif"  # You can change this path
        )
        
        # Level transition persistence
        self.last_successful_password = ""
        self.is_transitioning = False
        self.accumulated_rules = []  # Rules from all previously completed levels
        self.used_rules = set()  # Track rules that have been used in any level
        self.current_level_rules = []  # Rules found in the current level only (resets each level)
        
        # Setup programmatic interactables from configuration
        setup_level_interactables()
    
    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Handle other UI events
            ui_handled = False
            
            # Let password UI handle events first
            if self.password_ui.handle_event(event):
                ui_handled = True
            
            # Let rules display UI handle events
            if not ui_handled and self.rules_ui.handle_event(event):
                ui_handled = True
            
            # If UI handled the event, skip the rest of the processing for this event
            if ui_handled:
                continue
            
            elif event.type == pygame.MOUSEMOTION:
                # Update mouse position for debug coordinates
                self.mouse_x, self.mouse_y = event.pos
                self._update_mouse_tile_coords()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_mouse_click(event.pos)
            
            elif event.type == pygame.KEYDOWN:
                # Level navigation
                if event.key == pygame.K_n or event.key == pygame.K_RIGHT:
                    if self.level_manager.load_next_level():
                        # Move player to starting point of new level
                        start_x, start_y = self.level_manager.get_level_starting_point()
                        self.player.set_position(start_x, start_y)
                        self.load_level_interactables()
                
                elif event.key == pygame.K_p or event.key == pygame.K_LEFT:
                    if self.level_manager.load_previous_level():
                        # Move player to starting point of new level
                        start_x, start_y = self.level_manager.get_level_starting_point()
                        self.player.set_position(start_x, start_y)
                        self.load_level_interactables()
                
                elif event.key == pygame.K_r:
                    # Reload current level
                    current_name = self.level_manager.current_level_name
                    if current_name:
                        if self.level_manager.load_level(current_name):
                            # Move player to starting point
                            start_x, start_y = self.level_manager.get_level_starting_point()
                            self.player.set_position(start_x, start_y)
                            self.load_level_interactables()
                
                # Debug toggles
                elif event.key == pygame.K_F1:
                    self.show_debug = not self.show_debug
                
                elif event.key == pygame.K_F2:
                    self.smooth_camera = not self.smooth_camera
                
                elif event.key == pygame.K_F3:
                    # Toggle coordinate display
                    self.show_coordinates = not self.show_coordinates
                
                elif event.key == pygame.K_F4:
                    # Toggle creation mode
                    self.creation_mode = not self.creation_mode
                    if not self.creation_mode:
                        self.selected_tiles.clear()
                        self.delete_mode = False
                    self.message_ui.show_message(
                        f"Creation mode: {'ON' if self.creation_mode else 'OFF'} ({self.creation_type})", 2000
                    )
                
                elif event.key == pygame.K_TAB and self.creation_mode:
                    # Cycle between note, door, and delete modes
                    if self.creation_type == "note":
                        self.creation_type = "door"
                        self.delete_mode = False
                    elif self.creation_type == "door":
                        self.creation_type = "delete"
                        self.delete_mode = True
                    else:  # delete mode
                        self.creation_type = "note"
                        self.delete_mode = False
                    
                    # Clear selection when switching modes
                    self.selected_tiles.clear()
                    
                    mode_text = "DELETE" if self.delete_mode else self.creation_type.upper()
                    self.message_ui.show_message(f"Creation mode: {mode_text}", 2000)
                
                elif event.key == pygame.K_F5:
                    # Toggle speed debug
                    self.show_speed_debug = not self.show_speed_debug
                    self.message_ui.show_message(
                        f"Speed debug: {'ON' if self.show_speed_debug else 'OFF'}", 2000
                    )
                
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                
                # Speed controls (when speed debug is on)
                elif event.key == pygame.K_LEFTBRACKET and self.show_speed_debug:
                    # Decrease speed with [
                    self.player.adjust_speed(-self.player.speed_increment)
                    self.message_ui.show_message(f"Speed: {self.player.speed:.1f}", 1000)

                elif event.key == pygame.K_RIGHTBRACKET and self.show_speed_debug:
                    # Increase speed with ]
                    self.player.adjust_speed(self.player.speed_increment)
                    self.message_ui.show_message(f"Speed: {self.player.speed:.1f}", 1000)

                elif event.key == pygame.K_BACKSLASH and self.show_speed_debug:
                    # Reset speed to default with \
                    self.player.reset_speed()
                    self.message_ui.show_message(f"Speed reset to: {self.player.speed:.1f}", 1000)
                
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
                
                elif event.key == pygame.K_i and self.show_coordinates:
                    # Show programmatic interactables info for current level
                    self._show_interactables_info()
                
                elif event.key == pygame.K_x and self.show_coordinates:
                    # Copy current mouse coordinates to console
                    self._copy_mouse_coordinates()
                
                elif event.key == pygame.K_DELETE and self.show_coordinates:
                    # Clean up duplicate interactables
                    self._clean_duplicate_interactables()
                
                elif event.key == pygame.K_z and self.show_coordinates:
                    # Force reload level from file (useful for testing saved interactables)
                    current_name = self.level_manager.current_level_name
                    if current_name:
                        if self.level_manager.load_level(current_name):
                            self.load_level_interactables()
                            print(f"Force reloaded level '{current_name}' from file")
                            self.message_ui.show_message(f"Reloaded '{current_name}' from file", 2000)
                        else:
                            print(f"Failed to reload level '{current_name}' from file")
                            self.message_ui.show_message(f"Failed to reload '{current_name}'", 2000)
                    else:
                        self.message_ui.show_message("No level loaded", 2000)
                
                elif event.key == pygame.K_RETURN and self.creation_mode:
                    # Create interactable from selected tiles and save to JSON (not in delete mode)
                    if not self.delete_mode:
                        self._create_and_save_interactable()
                    else:
                        self.message_ui.show_message("Cannot create in delete mode - use TAB to switch modes", 2000)
        
        return True
    
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
                    self.message_ui.show_message(f"Deleted interactable at ({self.mouse_tile_x}, {self.mouse_tile_y})", 2000)
                else:
                    self.message_ui.show_message("No interactable found at this position", 1500)
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
                self.message_ui.show_message("Error during interaction", 2000)
    
    def _create_and_save_interactable(self):
        """Create interactable from selected tiles and save permanently to JSON"""
        if not self.selected_tiles:
            self.message_ui.show_message("No tiles selected!", 2000)
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
                
                self.message_ui.show_message(
                    f"Created {success_count} door(s)!", 3000
                )
            else:
                self.message_ui.show_message("Failed to create doors!", 2000)
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
                
                self.message_ui.show_message(
                    f"Saved {len(self.selected_tiles)} tiles as permanent interactables!", 3000
                )
            else:
                self.message_ui.show_message("Failed to save interactables!", 2000)
        
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
    
    def _draw_compass(self):
        """Draw a 2D pixelated circular compass with decorations"""
        compass_area_size = 64  # Overall square area the compass will occupy
        pixel_scale = 2         # Each 'pixel' of our art will be pixel_scale x pixel_scale screen pixels
        
        base_compass_x = self.screen_width - compass_area_size - 15 # Adjusted for new size
        base_compass_y = 85  # Below zoom indicator, adjusted
        if self.show_speed_debug:
            base_compass_y += 35 # Adjusted

        center_x = base_compass_x + compass_area_size // 2
        center_y = base_compass_y + compass_area_size // 2

        # --- Draw Pixelated Circular Compass Body ---
        radius_pixels = 15  # Radius of the circle in 'pixel' units
        
        # Colors
        body_color_dark = (30, 30, 30)    # Dark core
        body_color_mid = (50, 50, 50)      # Main body
        body_color_light = (80, 80, 80)    # Highlight/border accent
        border_color = (120, 120, 120)     # Outer border

        # Draw the circle pixel by pixel
        for y_offset_px in range(-radius_pixels -1, radius_pixels + 2):
            for x_offset_px in range(-radius_pixels -1, radius_pixels + 2):
                dist_sq = x_offset_px**2 + y_offset_px**2
                px = center_x + x_offset_px * pixel_scale
                py = center_y + y_offset_px * pixel_scale

                # Outer Border (slightly thicker circle)
                if radius_pixels**2 <= dist_sq < (radius_pixels + 1.5)**2:
                    pygame.draw.rect(self.screen, border_color, (px, py, pixel_scale, pixel_scale))
                # Main Body (filled circle)
                elif dist_sq < radius_pixels**2:
                    # Basic shading: darker towards top-left, lighter bottom-right (subtle)
                    if x_offset_px < -radius_pixels * 0.5 and y_offset_px < -radius_pixels * 0.5:
                        color_to_use = body_color_dark
                    elif x_offset_px > radius_pixels * 0.5 and y_offset_px > radius_pixels * 0.5:
                        color_to_use = body_color_light
                    else:
                        color_to_use = body_color_mid
                    pygame.draw.rect(self.screen, color_to_use, (px, py, pixel_scale, pixel_scale))
        
        # Decorative inner ring/crosshairs (optional)
        inner_ring_color = (70, 70, 70)
        for i_px in range(-radius_pixels, radius_pixels + 1):
            # Horizontal line
            if abs(i_px * pixel_scale) < radius_pixels * pixel_scale * 0.7:
                 pygame.draw.rect(self.screen, inner_ring_color, (center_x + i_px * pixel_scale - pixel_scale//2, center_y - pixel_scale//2, pixel_scale, pixel_scale))
            # Vertical line
            if abs(i_px * pixel_scale) < radius_pixels * pixel_scale * 0.7:
                 pygame.draw.rect(self.screen, inner_ring_color, (center_x - pixel_scale//2, center_y + i_px * pixel_scale - pixel_scale//2, pixel_scale, pixel_scale))


        nearest_door = self._get_nearest_door_position()

        if nearest_door:
            angle = self._calculate_direction_to_door(nearest_door)
            needle_color_main = (255, 50, 50) # Bright Red
            needle_color_accent = (200, 0, 0) # Darker Red for accent/shadow
            
            # --- Updated Needle Tail Colors ---
            needle_tail_color_main = (220, 220, 220)  # Main light grey/white
            needle_tail_color_accent = (170, 170, 170) # Slightly darker grey for accent
            
            needle_front_len_px = 10 # in 'pixels'
            needle_tail_len_px = 6 # Slightly longer tail for better balance

            # Draw main part (front) - thicker
            for i in range(needle_front_len_px):
                dist = i * pixel_scale
                px = center_x + math.cos(angle) * dist
                py = center_y + math.sin(angle) * dist
                pygame.draw.rect(self.screen, needle_color_accent, (px - pixel_scale + pixel_scale//2, py - pixel_scale + pixel_scale//2, pixel_scale*2, pixel_scale*2))
                pygame.draw.rect(self.screen, needle_color_main, (px - pixel_scale, py - pixel_scale, pixel_scale*2, pixel_scale*2))

            # Arrowhead (more defined)
            tip_dist = needle_front_len_px * pixel_scale
            tip_x = center_x + math.cos(angle) * tip_dist
            tip_y = center_y + math.sin(angle) * tip_dist

            arrowhead_size_px = 3 
            for i_arrow in range(-arrowhead_size_px // 2 +1 , arrowhead_size_px // 2 + 2):
                offset_angle = angle + math.pi / 2 
                offset_dist = i_arrow * pixel_scale
                base_ax = center_x + math.cos(angle) * (tip_dist - 2*pixel_scale) + math.cos(offset_angle) * offset_dist
                base_ay = center_y + math.sin(angle) * (tip_dist - 2*pixel_scale) + math.sin(offset_angle) * offset_dist
                # Arrowhead accent (draw first)
                pygame.draw.rect(self.screen, needle_color_accent, (base_ax-pixel_scale+pixel_scale//2, base_ay-pixel_scale+pixel_scale//2, pixel_scale*2, pixel_scale*2))
                pygame.draw.rect(self.screen, needle_color_main, (base_ax-pixel_scale, base_ay-pixel_scale, pixel_scale*2, pixel_scale*2))
            # Tip of arrowhead (draw last to be on top)
            pygame.draw.rect(self.screen, needle_color_accent, (tip_x-pixel_scale+pixel_scale//2, tip_y-pixel_scale+pixel_scale//2, pixel_scale*2, pixel_scale*2)) 
            pygame.draw.rect(self.screen, needle_color_main, (tip_x-pixel_scale, tip_y-pixel_scale, pixel_scale*2, pixel_scale*2))

            # --- Draw Improved Needle Tail ---
            # Tail will be a 2-pixel wide rectangle with an accent
            for i in range(1, needle_tail_len_px + 1):
                dist = i * pixel_scale
                # Calculate base position for this segment of the tail
                base_tail_x = center_x + math.cos(angle + math.pi) * dist
                base_tail_y = center_y + math.sin(angle + math.pi) * dist

                # Draw the two main pixels for width
                # Pixel 1 (slightly to one side of the center line)
                px1 = base_tail_x + math.cos(angle + math.pi/2) * (pixel_scale / 2)
                py1 = base_tail_y + math.sin(angle + math.pi/2) * (pixel_scale / 2)
                pygame.draw.rect(self.screen, needle_tail_color_main, (px1 - pixel_scale//2, py1 - pixel_scale//2, pixel_scale, pixel_scale))
                
                # Pixel 2 (slightly to the other side)
                px2 = base_tail_x - math.cos(angle + math.pi/2) * (pixel_scale / 2)
                py2 = base_tail_y - math.sin(angle + math.pi/2) * (pixel_scale / 2)
                pygame.draw.rect(self.screen, needle_tail_color_main, (px2 - pixel_scale//2, py2 - pixel_scale//2, pixel_scale, pixel_scale))
                
                # Add an accent pixel in the middle of the two, slightly offset for depth
                if i > 1 : # Don't put accent right at the pivot
                    accent_tail_x = base_tail_x + pixel_scale//4 # Offset for accent
                    accent_tail_y = base_tail_y + pixel_scale//4 # Offset for accent
                    pygame.draw.rect(self.screen, needle_tail_color_accent, (accent_tail_x - pixel_scale//2, accent_tail_y - pixel_scale//2, pixel_scale, pixel_scale))

            # Center Pivot (more decorative)
            pygame.draw.rect(self.screen, (80, 80, 80), (center_x - pixel_scale, center_y - pixel_scale, pixel_scale*2, pixel_scale*2))
            pygame.draw.rect(self.screen, (255,255,255), (center_x - pixel_scale//2, center_y - pixel_scale//2, pixel_scale, pixel_scale))
            
            font = pygame.font.Font(None, 18)
            label_text = "DOOR"
            label_surface = font.render(label_text, True, (230, 230, 230))
            label_rect = label_surface.get_rect(centerx=center_x, y=base_compass_y + compass_area_size + 3)
            outline_surface = font.render(label_text, True, (0,0,0))
            self.screen.blit(outline_surface, (label_rect.x + 1, label_rect.y + 1))
            self.screen.blit(label_surface, label_rect)

        else:
            # --- Default Pixelated Circular Compass (No Doors) ---
            dir_color_cardinal = (200, 200, 200)
            dir_color_inter = (140, 140, 140)
            marker_len_px = 3 # Length of cardinal markers from edge

            # Cardinal direction markers (lines from the edge inwards)
            for i in range(marker_len_px):
                dist_from_edge = i * pixel_scale
                # N
                pygame.draw.rect(self.screen, dir_color_cardinal, (center_x - pixel_scale//2, base_compass_y + (radius_pixels - 12)*pixel_scale + dist_from_edge, pixel_scale, pixel_scale))
                # S
                pygame.draw.rect(self.screen, dir_color_cardinal, (center_x - pixel_scale//2, base_compass_y + (radius_pixels + 10)*pixel_scale - dist_from_edge - pixel_scale*2, pixel_scale, pixel_scale))
                # E
                pygame.draw.rect(self.screen, dir_color_cardinal, (base_compass_x + (radius_pixels + 10)*pixel_scale - dist_from_edge - pixel_scale*2, center_y - pixel_scale//2, pixel_scale, pixel_scale))
                # W
                pygame.draw.rect(self.screen, dir_color_cardinal, (base_compass_x + (radius_pixels - 12)*pixel_scale + dist_from_edge, center_y - pixel_scale//2, pixel_scale, pixel_scale))

            # Intercardinal markers (single pixels)
            inter_dist_factor = 0.707 * (radius_pixels -1) # approx sqrt(2)/2 for 45 deg
            inter_marker_positions = [
                (center_x + inter_dist_factor * pixel_scale, center_y - inter_dist_factor * pixel_scale),
                (center_x + inter_dist_factor * pixel_scale, center_y + inter_dist_factor * pixel_scale),
                (center_x - inter_dist_factor * pixel_scale, center_y + inter_dist_factor * pixel_scale),
                (center_x - inter_dist_factor * pixel_scale, center_y - inter_dist_factor * pixel_scale),
            ]
            for pos_x, pos_y in inter_marker_positions:
                 pygame.draw.rect(self.screen, dir_color_inter, (pos_x - pixel_scale//2, pos_y - pixel_scale//2, pixel_scale, pixel_scale))

            # Center Pivot
            pygame.draw.rect(self.screen, (80, 80, 80), (center_x - pixel_scale, center_y - pixel_scale, pixel_scale*2, pixel_scale*2))
            pygame.draw.rect(self.screen, (255,255,255), (center_x - pixel_scale//2, center_y - pixel_scale//2, pixel_scale, pixel_scale))

            font = pygame.font.Font(None, 18)
            label_text = "COMPASS"
            label_surface = font.render(label_text, True, (180, 180, 180))
            label_rect = label_surface.get_rect(centerx=center_x, y=base_compass_y + compass_area_size + 3)
            outline_surface = font.render(label_text, True, (0,0,0))
            self.screen.blit(outline_surface, (label_rect.x + 1, label_rect.y + 1))
            self.screen.blit(label_surface, label_rect)
            
    def update(self):
        """Update game state"""
        if self.paused or self.password_ui.visible:
            self.message_ui.update()
            self.matrix_background.update()
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
        
        # Update UI components
        self.message_ui.update()
        
        # Update matrix background animation
        self.matrix_background.update()
        
        # Check for nearby interactables
        self.check_nearby_interactables()
    
    def render(self):
        """Render the game"""
        # Fill screen with black background
        self.screen.fill((0, 0, 0))
        
        # Render level with layered sprites
        self.level_manager.render_level(debug_info=self.show_debug)
        
        # Always draw proximity hints for nearby interactables (even when F3 is off)
        self._draw_proximity_hints()
        
        # Draw existing interactables debug outlines when coordinates are shown
        if self.show_coordinates:
            self._draw_existing_interactables()
        
        # Draw selected tiles in creation mode
        if self.creation_mode:
            self._draw_selected_tiles()
        
        # Render player
        self.player.render(self.screen, self.level_manager.camera)
        
        # Draw coordinate debug info
        if self.show_coordinates:
            self._draw_coordinate_debug()
        
        # Draw speed debug info
        if self.show_speed_debug:
            self._draw_speed_debug()
        
        # Draw zoom level indicator
        self._draw_zoom_indicator()
        
        # Draw compass
        self._draw_compass()
        
        # Draw control instructions
        self._draw_instructions()
        
        # Render UI components
        self.rules_ui.render(self.current_level_rules)
        self.message_ui.render()
        self.password_ui.render()
        
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
    
    def _draw_speed_debug(self):
        """Draw speed debug information"""
        font = pygame.font.Font(None, 24)
        speed_text = f"Speed: {self.player.speed:.1f}"
        
        # Render text with outline for visibility
        text_surface = font.render(speed_text, True, (255, 255, 255))
        outline_surface = font.render(speed_text, True, (0, 0, 0))
        
        # Position in top-right corner
        text_width = text_surface.get_width()
        x_pos = self.screen_width - text_width - 20
        y_pos = 20
        
        # Draw outline and text
        self.screen.blit(outline_surface, (x_pos + 1, y_pos + 1))
        self.screen.blit(text_surface, (x_pos, y_pos))
    
    def _draw_zoom_indicator(self):
        """Draw zoom level indicator in top-right corner"""
        font = pygame.font.Font(None, 32)
        zoom = self.level_manager.camera.zoom
        zoom_text = f"Zoom: {zoom:.1f}x"
        
        # Render text with outline for visibility
        text_surface = font.render(zoom_text, True, (255, 255, 255))
        outline_surface = font.render(zoom_text, True, (0, 0, 0))
        
        # Position in top-right corner (adjust if speed debug is shown)
        text_width = text_surface.get_width()
        x_pos = self.screen_width - text_width - 20
        y_pos = 50 if self.show_speed_debug else 20  # Move down if speed debug is shown
        
        # Draw outline and text
        self.screen.blit(outline_surface, (x_pos + 1, y_pos + 1))
        self.screen.blit(text_surface, (x_pos, y_pos))
    
    def _draw_instructions(self):
        """Draw control instructions on screen"""
        font = pygame.font.Font(None, 20)
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
        
        if interaction_type == "note_collected":
            rule = result.get("rule", "")
            if rule:
                game_state.add_rule(rule, result.get("note_id"))
                # Also add to current level rules
                if rule not in self.current_level_rules:
                    self.current_level_rules.append(rule)
                self.message_ui.show_message(f"Rule collected: {rule}", 3000)
            
        elif interaction_type == "note_already_collected":
            message = result.get("message", "Already read this note.")
            self.message_ui.show_message(message, 2000)
            
        elif interaction_type == "empty_interactable":
            message = result.get("message", "There's nothing here.")
            self.message_ui.show_message(message, 2000)
            
        elif interaction_type == "door_locked":
            message = result.get("message", "Door is locked.")
            self.message_ui.show_message(message, 3000)
            
        elif interaction_type == "door_password_prompt":
            # Show password UI with preserved password if available
            rules = result.get("rules", [])
            collected_rules = result.get("collected_rules", [])
            door = result.get("door")
            
            # Combine accumulated rules from previous levels with current level collected rules
            combined_collected_rules = self.accumulated_rules.copy()
            for rule in collected_rules:
                if rule not in combined_collected_rules:
                    combined_collected_rules.append(rule)
            
            self.password_ui.show(rules, door, self.handle_password_result, combined_collected_rules, self.last_successful_password, self.handle_password_ui_close)
            
        elif interaction_type == "door_open":
            message = result.get("message", "Door is open.")
            self.message_ui.show_message(message, 2000)
            
        elif interaction_type == "level_transition":
            # Handle level transition
            next_level = result.get("next_level")
            message = result.get("message", f"Entering {next_level}...")
            self.message_ui.show_message(message, 2000)
            
            if next_level:
                self.transition_to_level(next_level)
    
    def handle_password_result(self, result: Dict[str, Any]):
        """Handle password attempt results"""
        if result.get("success", False):
            # Check if this is a level transition
            if result.get("type") == "level_transition":
                next_level = result.get("next_level")
                message = result.get("message", f"Entering {next_level}...")
                self.message_ui.show_message(message, 2000)
                
                # Store the successful password and set transition flag
                if self.password_ui.password_input:
                    self.last_successful_password = self.password_ui.password_input.text
                
                # Accumulate rules from current level (avoid duplicates)
                current_level_rules = self.password_ui.rules if self.password_ui.rules else []
                for rule in current_level_rules:
                    if rule != "????" and rule not in self.accumulated_rules:
                        self.accumulated_rules.append(rule)
                        print(f"Accumulated rule: {rule}")
                
                print(f"Total accumulated rules: {len(self.accumulated_rules)}")
                for i, rule in enumerate(self.accumulated_rules, 1):
                    print(f"  {i}. {rule}")
                
                self.is_transitioning = True
                
                if next_level:
                    self.transition_to_level(next_level)
            else:
                self.message_ui.show_message("Door opened successfully!", 3000)
        else:
            message = result.get("message", "Password incorrect.")
            self.message_ui.show_message(message, 3000)
    
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
            self.message_ui.show_message("No level loaded!", 2000)
            return
        
        level_name = self.level_manager.current_level_name or "unknown"
        programmatic = interactable_manager.list_programmatic_interactables(level_name)
        
        if level_name in programmatic and programmatic[level_name]:
            count = len(programmatic[level_name])
            self.message_ui.show_message(f"Level '{level_name}' has {count} programmatic interactables", 3000)
            
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
            self.message_ui.show_message(f"No programmatic interactables for '{level_name}'", 2000)
    
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
            
            self.message_ui.show_message(f"Coordinates ({self.mouse_tile_x}, {self.mouse_tile_y}) printed to console!", 2000)
        except Exception as e:
            print(f"Error copying mouse coordinates: {e}")
            self.message_ui.show_message("Error copying coordinates", 2000)
    
    def _clean_duplicate_interactables(self):
        """Clean up duplicate interactables"""
        success = interactable_manager.clean_duplicate_interactables()
        
        if success:
            # Reload the level to show the cleaned up interactables
            current_name = self.level_manager.current_level_name
            if current_name:
                self.level_manager.load_level(current_name)
                self.load_level_interactables()
            
            self.message_ui.show_message("Duplicate interactables cleaned up!", 3000)
        else:
            self.message_ui.show_message("Failed to clean up duplicates!", 2000)
    
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
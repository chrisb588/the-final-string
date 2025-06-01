import pygame
import os
from typing import Dict, List, Optional, Tuple, Any
from .loader import LevelLoader, Level

class TileSprite(pygame.sprite.Sprite):
    """Sprite class for individual tiles that can be layered"""
    
    def __init__(self, tile_data: Dict[str, Any], world_x: int, world_y: int, 
                 tile_surface: pygame.Surface, layer_depth: int):
        super().__init__()
        self.image = tile_surface
        self.rect = pygame.Rect(world_x, world_y, tile_surface.get_width(), tile_surface.get_height())
        self.world_pos = (world_x, world_y)
        self.tile_data = tile_data
        self.layer_depth = layer_depth
        
        # Store original position for camera calculations
        self._original_rect = self.rect.copy()
    
    def update_screen_position(self, camera_x: int, camera_y: int, zoom: float = 1.0):
        """Update sprite position based on camera offset and zoom"""
        # Calculate position relative to camera
        world_x = self._original_rect.x - camera_x
        world_y = self._original_rect.y - camera_y
        
        # Apply zoom scaling
        self.rect.x = int(world_x * zoom)
        self.rect.y = int(world_y * zoom)
        
        # Scale the sprite size if zoomed
        if zoom != 1.0:
            original_size = self._original_rect.size
            new_width = int(original_size[0] * zoom)
            new_height = int(original_size[1] * zoom)
            self.rect.width = new_width
            self.rect.height = new_height
            
            # Scale the image
            if hasattr(self, '_original_image'):
                self.image = pygame.transform.scale(self._original_image, (new_width, new_height))
            else:
                # Store original image for future scaling
                self._original_image = self.image.copy()
                self.image = pygame.transform.scale(self._original_image, (new_width, new_height))
        else:
            # Reset to original size and image
            self.rect.size = self._original_rect.size
            if hasattr(self, '_original_image'):
                self.image = self._original_image.copy()

class LayeredTileRenderer:
    """Enhanced tile renderer using pygame's LayeredUpdates for proper layering"""
    
    def __init__(self, sprite_sheet_path: str = "assets/images/spritesheets"):
        self.sprite_sheet_path = sprite_sheet_path
        self.sprite_sheets = {}
        self.tile_surfaces = {}  # Cache for individual tile surfaces
    
    def load_sprite_sheet(self, filename: str) -> Optional[pygame.Surface]:
        """Load a sprite sheet image"""
        if filename in self.sprite_sheets:
            return self.sprite_sheets[filename]
        
        try:
            path = os.path.join(self.sprite_sheet_path, filename)
            surface = pygame.image.load(path).convert_alpha()
            self.sprite_sheets[filename] = surface
            print(f"Loaded sprite sheet: {filename}")
            return surface
        except pygame.error as e:
            print(f"Error loading sprite sheet {filename}: {e}")
            return None
    
    def get_sprite_sheet_for_level(self, level_name: str) -> str:
        """Get the appropriate sprite sheet filename for a level"""
        if level_name and level_name.startswith("level-"):
            parts = level_name.split("-")
            if len(parts) >= 2:
                level_base = f"{parts[0]}-{parts[1]}"
                return f"{level_base}.png"
        
        return "level-1.png"  # Default fallback
    
    def get_tile_surface(self, tile_id: str, tile_size: int, level_name: str = None) -> Optional[pygame.Surface]:
        """Get a surface for a specific tile ID from the appropriate sprite sheet"""
        sprite_sheet_filename = self.get_sprite_sheet_for_level(level_name)
        cache_key = f"{sprite_sheet_filename}_{tile_id}_{tile_size}"
        
        if cache_key in self.tile_surfaces:
            return self.tile_surfaces[cache_key]
        
        sheet = self.load_sprite_sheet(sprite_sheet_filename)
        if not sheet:
            print(f"Failed to load sprite sheet {sprite_sheet_filename} for tile {tile_id}")
            return None
        
        try:
            tile_id_int = int(tile_id)
            tiles_per_row = sheet.get_width() // tile_size
            
            if tiles_per_row <= 0:
                print(f"Invalid sprite sheet dimensions for {sprite_sheet_filename}")
                return None
            
            tile_x = (tile_id_int % tiles_per_row) * tile_size
            tile_y = (tile_id_int // tiles_per_row) * tile_size
            
            if (tile_x + tile_size <= sheet.get_width() and 
                tile_y + tile_size <= sheet.get_height()):
                
                sprite_tile = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                sprite_tile.blit(sheet, (0, 0), (tile_x, tile_y, tile_size, tile_size))
                
                self.tile_surfaces[cache_key] = sprite_tile
                return sprite_tile
            else:
                print(f"Tile {tile_id} is outside sprite sheet bounds for {sprite_sheet_filename}")
                return None
                
        except (ValueError, TypeError):
            print(f"Non-numeric tile ID: {tile_id}")
            return None
    
    def get_layer_depth(self, layer_name: str) -> int:
        """Get the render depth for a layer (lower numbers render first)"""
        return self.layer_depths.get(layer_name, 50)  # Default middle depth

class Camera:
    """Camera system for following targets and managing viewport (Stardew Valley style)"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.x = 0
        self.y = 0
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.target_x = 0
        self.target_y = 0
        self.follow_speed = 0.1  # For smooth camera following
        
        # Zoom functionality
        self.zoom = 2.0  # Current zoom level (1.0 = normal, 2.0 = 2x zoom, 0.5 = zoomed out)
        self.min_zoom = 0.25  # Minimum zoom (zoomed out)
        self.max_zoom = 4.0   # Maximum zoom (zoomed in)
        self.zoom_speed = 0.1  # How fast zoom changes
        
        # Camera bounds for keeping player centered (adjusted for zoom)
        self.half_screen_width = screen_width // 2
        self.half_screen_height = screen_height // 2
    
    def update(self, target_x: int, target_y: int, level_width: int, level_height: int, smooth: bool = False):
        """Update camera position to follow target (Stardew Valley style)"""
        # Get effective screen size accounting for zoom
        effective_width, effective_height = self.get_effective_screen_size()
        half_effective_width = effective_width // 2
        half_effective_height = effective_height // 2
        
        # Calculate desired camera position to center the player
        desired_camera_x = target_x - half_effective_width
        desired_camera_y = target_y - half_effective_height
        
        # Calculate camera bounds based on level size
        # If level is smaller than effective screen, center the level
        if level_width <= effective_width:
            # Center the level horizontally
            camera_x = -(effective_width - level_width) // 2
        else:
            # Normal clamping for levels larger than effective screen
            camera_x = max(0, min(desired_camera_x, level_width - effective_width))
        
        if level_height <= effective_height:
            # Center the level vertically
            camera_y = -(effective_height - level_height) // 2
        else:
            # Normal clamping for levels larger than effective screen
            camera_y = max(0, min(desired_camera_y, level_height - effective_height))
        
        if smooth:
            # Smooth camera following
            self.target_x = camera_x
            self.target_y = camera_y
            
            # Interpolate towards target
            self.x += (self.target_x - self.x) * self.follow_speed
            self.y += (self.target_y - self.y) * self.follow_speed
        else:
            # Instant camera following
            self.x = camera_x
            self.y = camera_y
    
    def apply(self, x: int, y: int) -> Tuple[int, int]:
        """Apply camera offset to world coordinates"""
        return (x - int(self.x), y - int(self.y))
    
    def zoom_in(self):
        """Zoom in (increase zoom level)"""
        self.zoom = min(self.max_zoom, self.zoom + self.zoom_speed)
    
    def zoom_out(self):
        """Zoom out (decrease zoom level)"""
        self.zoom = max(self.min_zoom, self.zoom - self.zoom_speed)
    
    def set_zoom(self, zoom_level: float):
        """Set zoom to a specific level"""
        self.zoom = max(self.min_zoom, min(self.max_zoom, zoom_level))
    
    def get_effective_screen_size(self) -> Tuple[int, int]:
        """Get the effective screen size in world coordinates (accounting for zoom)"""
        effective_width = int(self.screen_width / self.zoom)
        effective_height = int(self.screen_height / self.zoom)
        return effective_width, effective_height
    
    def get_visible_rect(self) -> pygame.Rect:
        """Get the visible area rectangle in world coordinates"""
        effective_width, effective_height = self.get_effective_screen_size()
        return pygame.Rect(int(self.x), int(self.y), effective_width, effective_height)

class LayeredLevelManager:
    """Enhanced level manager using LayeredUpdates for proper tile layering"""
    
    def __init__(self, screen: pygame.Surface, sprite_sheet_path: str = "assets/images/spritesheets"):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Initialize subsystems
        self.loader = LevelLoader()
        self.renderer = LayeredTileRenderer(sprite_sheet_path)
        self.camera = Camera(self.screen_width, self.screen_height)
        
        # Layered sprite groups
        self.tile_sprites = pygame.sprite.LayeredUpdates()
        self.visible_sprites = pygame.sprite.Group()  # Sprites currently visible on screen
        
        # Current level state
        self.current_level = None
        self.current_level_name = None
        
        # Level navigation
        self.available_levels = []
        self.current_level_index = 0
        
        # Performance settings
        self.cull_offscreen_sprites = True
        self.sprite_culling_margin = 64  # Extra pixels around screen to keep sprites active
        
        self.refresh_level_list()
    
    def refresh_level_list(self):
        """Refresh the list of available levels"""
        self.available_levels = self.loader.get_available_levels()
        print(f"Found {len(self.available_levels)} levels: {self.available_levels}")
    
    def load_level(self, level_name: str) -> bool:
        """Load a specific level and create sprite layers"""
        level = self.loader.load_level(level_name)
        if not level:
            return False
        
        self.current_level = level
        self.current_level_name = level_name
        
        # Clear existing sprites
        self.tile_sprites.empty()
        self.visible_sprites.empty()
        
        # Create tile sprites for all layers
        self._create_tile_sprites()
        
        # Update level index
        if level_name in self.available_levels:
            self.current_level_index = self.available_levels.index(level_name)
        
        print(f"Level loaded: {level_name} ({level.map_width}x{level.map_height}) - {len(self.tile_sprites)} sprites created")
        print(f"Starting point: {level.get_starting_point()} (pixels), {level.get_starting_point_tiles()} (tiles)")
        return True
    
    def get_level_starting_point(self) -> Tuple[int, int]:
        """Get the starting point for the current level in pixel coordinates"""
        if self.current_level:
            return self.current_level.get_starting_point()
        return (100, 100)  # Default fallback
    
    def get_current_level_path(self) -> Optional[str]:
        """Get the file path of the current level for saving"""
        if self.current_level:
            return self.current_level.level_path
        return None
    
    def _create_tile_sprites(self):
        """Create TileSprite objects for all tiles in all layers"""
        if not self.current_level:
            return
        
        # Process layers in reverse order so first layer in JSON renders last
        # This gives us the exact ordering from your level data
        for layer_index, layer_data in enumerate(reversed(self.current_level.raw_data.get('layers', []))):
            # Use layer index directly as depth - higher index = renders later
            depth = layer_index * 10  # Use larger gaps between layers
            
            # Get layer name for filtering
            layer_name = layer_data.get('name', '')
            
            # Create sprites for each tile in this layer
            for tile_data in layer_data['tiles']:
                # Skip creating sprites for empty interactables (they shouldn't be visible)
                if (layer_name == "interactables" and 
                    tile_data.get("type") in ["empty", "multi_empty"] and 
                    not tile_data.get("rule")):
                    continue
                
                # Skip tiles without an id (some interactables might not have sprites)
                tile_id = tile_data.get('id')
                if not tile_id:
                    continue
                
                tile_surface = self.renderer.get_tile_surface(
                    tile_id, 
                    self.current_level.tile_size, 
                    self.current_level_name
                )
                
                if tile_surface:
                    world_x, world_y = self.current_level.tile_to_pixel(
                        tile_data['x'], tile_data['y']
                    )
                    
                    tile_sprite = TileSprite(
                        tile_data, world_x, world_y, tile_surface, depth
                    )
                    
                    # Add to layered group with layer index as depth
                    self.tile_sprites.add(tile_sprite, layer=depth)
    
    def load_next_level(self) -> bool:
        """Load the next level in the list"""
        if not self.available_levels:
            return False
        
        self.current_level_index = (self.current_level_index + 1) % len(self.available_levels)
        return self.load_level(self.available_levels[self.current_level_index])
    
    def load_previous_level(self) -> bool:
        """Load the previous level in the list"""
        if not self.available_levels:
            return False
        
        self.current_level_index = (self.current_level_index - 1) % len(self.available_levels)
        return self.load_level(self.available_levels[self.current_level_index])
    
    def load_first_level(self) -> bool:
        """Load the first available level"""
        if not self.available_levels:
            return False
        return self.load_level(self.available_levels[0])
    
    def update_camera(self, player_x: int, player_y: int, smooth: bool = False):
        """Update camera position to follow player"""
        if self.current_level:
            level_width, level_height = self.current_level.get_pixel_size()
            self.camera.update(player_x, player_y, level_width, level_height, smooth)
    
    def update(self):
        """Update all sprites and handle culling"""
        if not self.current_level:
            return
        
        # Update sprite positions based on camera
        camera_x, camera_y = int(self.camera.x), int(self.camera.y)
        zoom = self.camera.zoom
        
        # Clear visible sprites group
        self.visible_sprites.empty()
        
        if self.cull_offscreen_sprites:
            # Only update sprites that are potentially visible (accounting for zoom)
            effective_width, effective_height = self.camera.get_effective_screen_size()
            visible_rect = pygame.Rect(
                camera_x - self.sprite_culling_margin,
                camera_y - self.sprite_culling_margin,
                effective_width + 2 * self.sprite_culling_margin,
                effective_height + 2 * self.sprite_culling_margin
            )
            
            for sprite in self.tile_sprites:
                if sprite._original_rect.colliderect(visible_rect):
                    sprite.update_screen_position(camera_x, camera_y, zoom)
                    self.visible_sprites.add(sprite)
        else:
            # Update all sprites
            for sprite in self.tile_sprites:
                sprite.update_screen_position(camera_x, camera_y, zoom)
                self.visible_sprites.add(sprite)
    
    def render_level(self, debug_info: bool = False):
        """Render the current level using layered sprites"""
        if not self.current_level:
            return
        
        # Update sprites first
        self.update()
        
        # Render visible sprites in layer order
        if self.cull_offscreen_sprites:
            # Only draw visible sprites
            screen_rect = pygame.Rect(0, 0, self.screen_width, self.screen_height)
            visible_on_screen = [s for s in self.visible_sprites if s.rect.colliderect(screen_rect)]
            
            # Sort by layer depth for proper rendering order
            visible_on_screen.sort(key=lambda s: self.tile_sprites.get_layer_of_sprite(s))
            
            for sprite in visible_on_screen:
                self.screen.blit(sprite.image, sprite.rect)
        else:
            # Use LayeredUpdates built-in drawing (automatically handles layer order)
            on_screen_sprites = [s for s in self.visible_sprites 
                               if s.rect.colliderect(pygame.Rect(0, 0, self.screen_width, self.screen_height))]
            
            for sprite in on_screen_sprites:
                self.screen.blit(sprite.image, sprite.rect)
        
        # Debug information
        if debug_info:
            self._render_debug_info()
    
    def _render_debug_info(self):
        """Render debug information overlay"""
        if not self.current_level:
            return
        
        font = pygame.font.Font(None, 24)
        debug_texts = [
            f"Level: {self.current_level_name}",
            f"Total Sprites: {len(self.tile_sprites)}",
            f"Visible Sprites: {len(self.visible_sprites)}",
            f"Camera: ({int(self.camera.x)}, {int(self.camera.y)})",
            f"Zoom: {self.camera.zoom:.2f}x",
            f"Layers: {len(self.current_level.layers)}"
        ]
        
        y_offset = 10
        for text in debug_texts:
            surface = font.render(text, True, (255, 255, 255))
            # Add black outline for better visibility
            outline_surface = font.render(text, True, (0, 0, 0))
            self.screen.blit(outline_surface, (11, y_offset + 1))
            self.screen.blit(surface, (10, y_offset))
            y_offset += 25
    
    def check_collision(self, x: int, y: int) -> bool:
        """Check if there's a collision at world coordinates"""
        if not self.current_level:
            return False
        
        tile_x, tile_y = self.current_level.pixel_to_tile(x, y)
        return self.current_level.is_collision_at(tile_x, tile_y)
    
    def get_sprites_at_position(self, world_x: int, world_y: int) -> List[TileSprite]:
        """Get all tile sprites at a world position"""
        sprites_at_pos = []
        point = pygame.math.Vector2(world_x, world_y)
        
        for sprite in self.tile_sprites:
            if sprite._original_rect.collidepoint(point):
                sprites_at_pos.append(sprite)
        
        # Sort by layer depth (background to foreground)
        sprites_at_pos.sort(key=lambda s: self.tile_sprites.get_layer_of_sprite(s))
        return sprites_at_pos
    
    def get_level_info(self) -> Dict[str, Any]:
        """Get information about the current level"""
        if not self.current_level:
            return {}
        
        return {
            'name': self.current_level_name,
            'width': self.current_level.map_width,
            'height': self.current_level.map_height,
            'tile_size': self.current_level.tile_size,
            'pixel_size': self.current_level.get_pixel_size(),
            'layers': list(self.current_level.layers.keys()),
            'collision_layers': [layer.name for layer in self.current_level.get_collision_layers()],
            'total_sprites': len(self.tile_sprites),
            'visible_sprites': len(self.visible_sprites)
        }
    
    def set_layer_depths(self, depth_mapping: Dict[str, int]):
        """Update layer depth mapping and recreate sprites"""
        self.renderer.layer_depths.update(depth_mapping)
        if self.current_level:
            # Recreate sprites with new depths
            self._create_tile_sprites()
    
    def toggle_layer_visibility(self, layer_name: str, visible: bool):
        """Show or hide a specific layer"""
        layer_depth = self.renderer.get_layer_depth(layer_name)
        
        if visible:
            # Make layer visible by setting normal depth
            for sprite in self.tile_sprites:
                if (hasattr(sprite, 'tile_data') and 
                    sprite.layer_depth == layer_depth):
                    self.tile_sprites.change_layer(sprite, layer_depth)
        else:
            # Hide layer by moving to a very high depth or removing
            sprites_to_remove = []
            for sprite in self.tile_sprites:
                if (hasattr(sprite, 'tile_data') and 
                    sprite.layer_depth == layer_depth):
                    sprites_to_remove.append(sprite)
            
            for sprite in sprites_to_remove:
                self.tile_sprites.remove(sprite)
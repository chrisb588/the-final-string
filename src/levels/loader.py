import json
import pygame
import os
from typing import Dict, List, Tuple, Any, Optional

class TileLayer:
    """Represents a single layer of tiles in the map"""
    
    def __init__(self, name: str, tiles: List[Dict], collider: bool = False):
        self.name = name
        self.tiles = tiles
        self.collider = collider
        self.tile_dict = {}  # For quick lookup by position
        self._build_tile_dict()
    
    def _build_tile_dict(self):
        """Build a dictionary for quick tile lookup by position"""
        for tile in self.tiles:
            x, y = tile['x'], tile['y']
            self.tile_dict[(x, y)] = tile
    
    def get_tile_at(self, x: int, y: int) -> Optional[Dict]:
        """Get tile at specific coordinates"""
        return self.tile_dict.get((x, y))
    
    def has_tile_at(self, x: int, y: int) -> bool:
        """Check if there's a tile at specific coordinates"""
        return (x, y) in self.tile_dict

class Level:
    """Represents a complete level with all its layers and metadata"""
    
    def __init__(self, data: Dict[str, Any], level_path: str):
        self.level_path = level_path
        self.tile_size = data.get('tileSize', 16)
        self.map_width = data.get('mapWidth', 0)
        self.map_height = data.get('mapHeight', 0)
        
        # Store raw data for reference
        self.raw_data = data
        
        # Process starting point
        self.starting_point = self._parse_starting_point(data)
        
        # Process layers
        self.layers = {}  # Change to store with unique IDs
        self.layer_order = []  # Keep original order
        
        for idx, layer_data in enumerate(data.get('layers', [])):
            # Create unique layer ID using name and index
            layer_id = f"{layer_data['name']}_{idx}"
            layer = TileLayer(
                name=layer_data['name'],
                tiles=layer_data['tiles'],
                collider=layer_data.get('collider', False)
            )
            self.layers[layer_id] = layer
            self.layer_order.append(layer_id)
    
    def get_layer(self, name: str) -> Optional[TileLayer]:
        """Get a specific layer by name"""
        return self.layers.get(name)
    
    def get_collision_layers(self) -> List[TileLayer]:
        """Get all layers that have collision enabled"""
        return [layer for layer in self.layers.values() if layer.collider]
    
    def get_render_layers(self) -> List[TileLayer]:
        """Get all layers in exact JSON order"""
        return [self.layers[layer_id] for layer_id in self.layer_order]
    
    def is_collision_at(self, x: int, y: int) -> bool:
        """Check if there's a collision at the given tile coordinates"""
        for layer in self.get_collision_layers():
            if layer.has_tile_at(x, y):
                return True
        return False
    
    def get_pixel_size(self) -> Tuple[int, int]:
        """Get the level size in pixels"""
        return (self.map_width * self.tile_size, self.map_height * self.tile_size)
    
    def tile_to_pixel(self, tile_x: int, tile_y: int) -> Tuple[int, int]:
        """Convert tile coordinates to pixel coordinates"""
        return (tile_x * self.tile_size, tile_y * self.tile_size)
    
    def pixel_to_tile(self, pixel_x: int, pixel_y: int) -> Tuple[int, int]:
        """Convert pixel coordinates to tile coordinates"""
        return (pixel_x // self.tile_size, pixel_y // self.tile_size)
    
    def _parse_starting_point(self, data: Dict[str, Any]) -> Tuple[int, int]:
        """Parse starting point from level data"""
        # Check for explicit starting point in level data
        if 'startingPoint' in data:
            start_data = data['startingPoint']
            if isinstance(start_data, dict):
                x = start_data.get('x', 0)
                y = start_data.get('y', 0)
                # Convert tile coordinates to pixel coordinates
                return self.tile_to_pixel(x, y)
            elif isinstance(start_data, list) and len(start_data) >= 2:
                # Convert tile coordinates to pixel coordinates
                return self.tile_to_pixel(start_data[0], start_data[1])
        
        # Check for starting point in metadata
        if 'metadata' in data and 'startingPoint' in data['metadata']:
            start_data = data['metadata']['startingPoint']
            if isinstance(start_data, dict):
                x = start_data.get('x', 0)
                y = start_data.get('y', 0)
                return self.tile_to_pixel(x, y)
            elif isinstance(start_data, list) and len(start_data) >= 2:
                return self.tile_to_pixel(start_data[0], start_data[1])
        
        # Default starting point (center of map)
        center_x = (self.map_width // 2) * self.tile_size
        center_y = (self.map_height // 2) * self.tile_size
        return (center_x, center_y)
    
    def get_starting_point(self) -> Tuple[int, int]:
        """Get the starting point in pixel coordinates"""
        return self.starting_point
    
    def get_starting_point_tiles(self) -> Tuple[int, int]:
        """Get the starting point in tile coordinates"""
        return self.pixel_to_tile(self.starting_point[0], self.starting_point[1])

class LevelLoader:
    """Handles loading and parsing of level data"""
    
    def __init__(self, base_path: str = "src/levels/level-data"):
        self.base_path = base_path
        self.loaded_levels = {}  # Cache for loaded levels
    
    def load_level(self, level_name: str) -> Optional[Level]:
        """Load a level from JSON file"""
        # Check cache first
        if level_name in self.loaded_levels:
            return self.loaded_levels[level_name]
        
        # Construct file path
        level_file = f"{level_name}.json"
        level_path = os.path.join(self.base_path, level_file)
        
        try:
            # Load and parse JSON
            with open(level_path, 'r') as file:
                data = json.load(file)
            
            # Create level object
            level = Level(data, level_path)
            
            # Cache the level
            self.loaded_levels[level_name] = level
            
            print(f"Successfully loaded level: {level_name}")
            return level
            
        except FileNotFoundError:
            print(f"Error: Level file not found: {level_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in level file {level_path}: {e}")
            return None
        except Exception as e:
            print(f"Error loading level {level_name}: {e}")
            return None
    
    def reload_level(self, level_name: str) -> Optional[Level]:
        """Reload a level from disk, bypassing cache"""
        if level_name in self.loaded_levels:
            del self.loaded_levels[level_name]
        return self.load_level(level_name)
    
    def get_available_levels(self) -> List[str]:
        """Get list of available level files"""
        levels = []
        try:
            if os.path.exists(self.base_path):
                for file in os.listdir(self.base_path):
                    if file.endswith('.json'):
                        levels.append(file[:-5])  # Remove .json extension
        except Exception as e:
            print(f"Error scanning for levels: {e}")
        
        return sorted(levels)
    
    def validate_level_data(self, level: Level) -> List[str]:
        """Validate level data and return list of issues found"""
        issues = []
        
        # Check basic properties
        if level.tile_size <= 0:
            issues.append("Invalid tile size")
        
        if level.map_width <= 0 or level.map_height <= 0:
            issues.append("Invalid map dimensions")
        
        # Check layers
        if not level.layers:
            issues.append("No layers found")
        
        # Check for tiles outside map bounds
        for layer_name, layer in level.layers.items():
            for tile in layer.tiles:
                x, y = tile.get('x', -1), tile.get('y', -1)
                if x < 0 or x >= level.map_width or y < 0 or y >= level.map_height:
                    issues.append(f"Tile out of bounds in layer '{layer_name}': ({x}, {y})")
        
        return issues

# Helper functions for common operations
def load_single_level(level_name: str, base_path: str = "levels/level-data") -> Optional[Level]:
    """Convenience function to load a single level"""
    loader = LevelLoader(base_path)
    return loader.load_level(level_name)

def get_collision_map(level: Level) -> List[List[bool]]:
    """Generate a 2D collision map for pathfinding or AI"""
    collision_map = [[False for _ in range(level.map_width)] for _ in range(level.map_height)]
    
    for y in range(level.map_height):
        for x in range(level.map_width):
            collision_map[y][x] = level.is_collision_at(x, y)
    
    return collision_map
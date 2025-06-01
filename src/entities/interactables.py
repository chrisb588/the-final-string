import pygame
import sys
import os
import json
import random
from typing import Dict, Any, Optional, Callable, List, Set, Tuple

# Add the src directory to the path so we can import game_state
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game_state import game_state

class Interactable:
    """Base class for interactable objects"""
    
    def __init__(self, x: int, y: int, tile_id: str):
        self.x = x
        self.y = y
        self.tile_id = tile_id
        self.rect = pygame.Rect(x * 16, y * 16, 16, 16)
        
    def interact(self, player_x: int, player_y: int) -> Dict[str, Any]:
        """Handle interaction with this object"""
        return {"type": "none"}
    
    def is_near_player(self, player_x: int, player_y: int, distance: int = 20) -> bool:
        """Check if player is close enough to interact"""
        dx = abs(self.x - player_x)
        dy = abs(self.y - player_y)
        return dx <= distance and dy <= distance
    
    def contains_tile(self, x: int, y: int) -> bool:
        """Check if this interactable contains the given tile coordinates"""
        return self.x == x and self.y == y

class EmptyInteractable(Interactable):
    """An interactable that has no rule - just shows 'nothing here' message"""
    
    def __init__(self, x: int, y: int, tile_id: str):
        super().__init__(x, y, tile_id)
        self.collected = False  # Track if this has been interacted with
        
    def interact(self, player_x: int, player_y: int) -> Dict[str, Any]:
        """Show 'nothing here' message"""
        messages = [
            "There's nothing here.",
            "This spot seems empty.",
            "You find nothing of interest.",
            "Nothing useful here.",
            "This area appears to be empty."
        ]
        
        # Mark as collected/interacted with
        self.collected = True
        
        return {
            "type": "empty_interactable",
            "message": random.choice(messages)
        }

class MultiTileInteractable(Interactable):
    """An interactable that spans multiple tiles"""
    
    def __init__(self, tiles: Set[Tuple[int, int]], tile_id: str, interaction_type: str = "note"):
        # Use the first tile as the primary position
        first_tile = next(iter(tiles))
        super().__init__(first_tile[0], first_tile[1], tile_id)
        
        self.tiles = tiles
        self.interaction_type = interaction_type
        
        # Calculate bounding box for all tiles
        min_x = min(x for x, y in tiles)
        max_x = max(x for x, y in tiles)
        min_y = min(y for x, y in tiles)
        max_y = max(y for x, y in tiles)
        
        self.rect = pygame.Rect(
            min_x * 16, min_y * 16, 
            (max_x - min_x + 1) * 16, 
            (max_y - min_y + 1) * 16
        )
    
    def contains_tile(self, x: int, y: int) -> bool:
        """Check if this interactable contains the given tile coordinates"""
        return (x, y) in self.tiles
    
    def is_near_player(self, player_x: int, player_y: int, distance: int = 20) -> bool:
        """Check if player is close enough to interact with any tile in the group"""
        player_tile_x = int(player_x // 16)
        player_tile_y = int(player_y // 16)
        
        for tile_x, tile_y in self.tiles:
            dx = abs(tile_x - player_tile_x)
            dy = abs(tile_y - player_tile_y)
            if dx <= distance and dy <= distance:
                return True
        return False

class MultiTileNote(MultiTileInteractable):
    """A note that spans multiple tiles"""
    
    def __init__(self, tiles: Set[Tuple[int, int]], tile_id: str, rule: str):
        super().__init__(tiles, tile_id, "note")
        self.rule = rule
        self.collected = False
        
    def interact(self, player_x: int, player_y: int) -> Dict[str, Any]:
        """Collect the note and its rule"""
        if not self.collected:
            # Create a unique ID based on all tiles
            tile_coords = sorted(list(self.tiles))
            note_id = f"multi_note_{'_'.join(f'{x}_{y}' for x, y in tile_coords)}"
            
            if not game_state.has_note(note_id):
                game_state.add_rule(self.rule, note_id)
                self.collected = True
                return {
                    "type": "note_collected", 
                    "rule": self.rule,
                    "message": f"You found a rule: {self.rule} (covers {len(self.tiles)} tiles)"
                }
        
        return {
            "type": "note_already_collected",
            "message": "You already collected this note."
        }

class Note(Interactable):
    """A collectible note that contains a password rule"""
    
    def __init__(self, x: int, y: int, tile_id: str, rule: str):
        super().__init__(x, y, tile_id)
        self.rule = rule
        self.collected = False
        
    def interact(self, player_x: int, player_y: int) -> Dict[str, Any]:
        """Collect the note and its rule"""
        if not self.collected:
            note_id = f"note_{self.x}_{self.y}"
            if not game_state.has_note(note_id):
                game_state.add_rule(self.rule, note_id)
                self.collected = True
                return {
                    "type": "note_collected", 
                    "rule": self.rule,
                    "message": f"You found a rule: {self.rule}"
                }
        
        return {
            "type": "note_already_collected",
            "message": "You already collected this note."
        }

class Door(Interactable):
    """A door that requires password validation"""
    
    def __init__(self, x: int, y: int, tile_id: str, required_rules: int = 4, next_level: str = None):
        super().__init__(x, y, tile_id)
        self.required_rules = required_rules
        self.is_open = False
        self.level_metadata = None
        self.next_level = next_level  # Level to transition to when walking through
        
    def interact(self, player_x: int, player_y: int) -> Dict[str, Any]:
        """Handle door interaction - show password prompt"""
        # Get collected rules from game state
        collected_count = game_state.get_rules_count()
        collected_rules = game_state.get_rules()
        
        # Get all rules for this level from metadata (level-specific rules)
        all_rules = []
        if self.level_metadata and "rules" in self.level_metadata:
            all_rules = self.level_metadata["rules"]
        else:
            # Fallback to tutorial rules if no level metadata
            all_rules = game_state.rule_manager.get_tutorial_rules()
        
        # For display, show the level's rules (not the collected ones)
        # Mark collected rules with checkmarks
        display_rules = []
        for rule in all_rules:
            if rule in collected_rules:
                display_rules.append(rule)  # Show collected rule
            else:
                display_rules.append("????")  # Show placeholder for uncollected
        
        return {
            "type": "door_password_prompt",
            "message": f"Password required. You have {collected_count}/{self.required_rules} rules.",
            "rules": display_rules,
            "collected_rules": collected_rules,
            "door": self,
            "missing_count": self.required_rules - collected_count
        }
    
    def set_level_metadata(self, metadata: Dict[str, Any]):
        """Set level metadata for rule lookup"""
        self.level_metadata = metadata
    
    def set_required_rules(self, required_rules: int):
        """Set the required rules count (for accumulated rules from previous levels)"""
        self.required_rules = required_rules
    
    def try_password(self, password: str) -> Dict[str, Any]:
        """Try to open the door with a password"""
        validation_results = game_state.validate_password(password)
        is_valid = game_state.is_password_valid(password)
        
        if is_valid:
            self.is_open = True
            # If this door has a next_level, trigger level transition
            if self.next_level:
                return {
                    "type": "level_transition",
                    "message": f"Correct! Entering {self.next_level}...",
                    "success": True,
                    "next_level": self.next_level,
                    "validation_results": validation_results
                }
            else:
                return {
                    "type": "door_opened",
                    "message": "Correct! The door opens.",
                    "success": True,
                    "validation_results": validation_results
                }
        else:
            return {
                "type": "door_failed",
                "message": "Password doesn't meet all the requirements.",
                "success": False,
                "validation_results": validation_results
            }

class MultiTileEmptyInteractable(MultiTileInteractable):
    """A multi-tile interactable that has no rule"""
    
    def __init__(self, tiles: Set[Tuple[int, int]], tile_id: str):
        super().__init__(tiles, tile_id, "empty")
        self.collected = False  # Track if this has been interacted with
        
    def interact(self, player_x: int, player_y: int) -> Dict[str, Any]:
        """Show 'nothing here' message"""
        messages = [
            "There's nothing here.",
            "This area seems empty.",
            "You search the area but find nothing.",
            "Nothing useful in this spot.",
            "This place appears to be empty."
        ]
        
        # Mark as collected/interacted with
        self.collected = True
        
        return {
            "type": "empty_interactable",
            "message": random.choice(messages)
        }

class InteractableManager:
    """Manages all interactable objects in a level"""
    
    def __init__(self):
        self.interactables: List[Interactable] = []
        self.level_metadata = None
        self.programmatic_interactables = {}  # Store interactables defined in code by level name
        self.current_level_path = None  # Track current level file path
        
    def load_from_level_data(self, level_data: Dict[str, Any], used_rules: set = None):
        """Load interactables from level data"""
        self.interactables.clear()
        self.level_metadata = level_data.get("metadata", {})
        
        # ========================================
        # DYNAMIC RULE SELECTION
        # ========================================
        # If level has rule_count instead of specific rules, randomly select rules
        if "rule_count" in self.level_metadata and "rules" not in self.level_metadata:
            rule_count = self.level_metadata["rule_count"]
            
            # Special case for Level-0: use tutorial rules instead of extended rules
            level_name = self.level_metadata.get("name", "")
            
            # Check if this is Level-0 by name or by checking current level path
            is_level_0 = (level_name == "level-0" or 
                         (hasattr(self, 'current_level_path') and 
                          self.current_level_path and 
                          "level-0.json" in self.current_level_path))
            
            if is_level_0:
                # For Level-0, use tutorial rules
                selected_rules = game_state.rule_manager.get_tutorial_rules()[:rule_count]
                print(f"Using tutorial rules for Level-0 (selected {len(selected_rules)} rules):")
                for i, rule in enumerate(selected_rules, 1):
                    print(f"  {i}. {rule}")
            else:
                # For other levels, use randomized rules from extended_rules for dynamic selection, excluding used rules
                if used_rules is None:
                    used_rules = set()
                
                selected_rules = game_state.rule_manager.get_randomized_rules(rule_count, used_rules)
                print(f"Randomly selected {len(selected_rules)} rules for level (excluding {len(used_rules)} previously used):")
                for i, rule in enumerate(selected_rules, 1):
                    print(f"  {i}. {rule}")
            
            self.level_metadata["rules"] = selected_rules
        
        # ========================================
        # LEVEL TYPE DETECTION AND RULE LOADING
        # ========================================
        level_type = self._detect_level_type(level_data)
        
        for layer in level_data.get("layers", []):
            if layer.get("name") == "interactables":
                for tile in layer.get("tiles", []):
                    obj = self._create_interactable(tile, level_type)
                    if obj:
                        self.interactables.append(obj)
        
        # Add programmatically defined interactables for this level
        level_name = level_data.get("metadata", {}).get("name", "unknown")
        if level_name in self.programmatic_interactables:
            for interactable_def in self.programmatic_interactables[level_name]:
                obj = self._create_programmatic_interactable(interactable_def)
                if obj:
                    self.interactables.append(obj)
        
        # For levels that use rule_count, reset and randomly assign rules
        if "rule_count" in self.level_metadata:
            self._randomly_assign_rules_for_level()
    
    def set_current_level_path(self, level_path: str):
        """Set the current level file path for saving"""
        self.current_level_path = level_path
    
    def save_interactables_to_level_file(self, tiles: Set[Tuple[int, int]], tile_id: str = "25") -> bool:
        """Save interactables directly to the level JSON file (without rules - purely for positioning)"""
        if not self.current_level_path:
            print("No current level path set!")
            return False
        
        try:
            # Load the current level file
            with open(self.current_level_path, 'r') as f:
                level_data = json.load(f)
            
            # Find or create the interactables layer - handle multiple interactables layers
            interactables_layer = None
            duplicate_layers = []
            
            for i, layer in enumerate(level_data.get("layers", [])):
                if layer.get("name") == "interactables":
                    if interactables_layer is None:
                        interactables_layer = layer
                        print(f"Found primary interactables layer at index {i}")
                    else:
                        duplicate_layers.append((i, layer))
                        print(f"Found duplicate interactables layer at index {i}")
            
            # If there are duplicate layers, merge them into the first one
            if duplicate_layers:
                print(f"Merging {len(duplicate_layers)} duplicate interactables layers into primary layer")
                for layer_index, duplicate_layer in duplicate_layers:
                    # Add tiles from duplicate layer to primary layer
                    for tile in duplicate_layer.get("tiles", []):
                        interactables_layer["tiles"].append(tile)
                
                # Remove duplicate layers (in reverse order to maintain indices)
                for layer_index, _ in reversed(duplicate_layers):
                    del level_data["layers"][layer_index]
                    print(f"Removed duplicate interactables layer at index {layer_index}")
            
            if not interactables_layer:
                # Create new interactables layer
                interactables_layer = {
                    "name": "interactables",
                    "tiles": [],
                    "collider": False
                }
                level_data["layers"].append(interactables_layer)
                print("Created new interactables layer")
            
            # Group adjacent tiles
            groups = self._group_adjacent_tiles_static(tiles)
            
            # Get existing coordinates to prevent duplicates
            existing_coords = set()
            for tile in interactables_layer["tiles"]:
                existing_coords.add((tile["x"], tile["y"]))
            
            # Add new interactables for each group
            added_count = 0
            for group in groups:
                # Skip if any tile in this group already exists
                if any((x, y) in existing_coords for x, y in group):
                    print(f"Skipping group {group} - tiles already exist")
                    continue
                
                if len(group) == 1:
                    # Single tile interactable
                    x, y = next(iter(group))
                    new_tile = {
                        "x": x,
                        "y": y,
                        "type": "empty"
                    }
                    # Don't add tile_id for empty interactables to keep them invisible
                    # This prevents them from overriding existing background sprites
                    
                    interactables_layer["tiles"].append(new_tile)
                    added_count += 1
                    print(f"Added single tile interactable at ({x}, {y})")
                else:
                    # Multi-tile interactable - create one entry for the whole group
                    coordinates = list(group)
                    first_coord = coordinates[0]
                    new_tile = {
                        "x": first_coord[0],
                        "y": first_coord[1],
                        "type": "multi_empty",
                        "coordinates": coordinates
                    }
                    # Don't add tile_id for empty interactables to keep them invisible
                    # This prevents them from overriding existing background sprites
                    
                    interactables_layer["tiles"].append(new_tile)
                    added_count += 1
                    print(f"Added multi-tile interactable with {len(group)} tiles starting at {first_coord}")
            
            if added_count == 0:
                print("No new interactables were added (all positions already exist)")
                return False
            
            # Save the modified level file
            with open(self.current_level_path, 'w') as f:
                json.dump(level_data, f, indent=2)
            
            print(f"Successfully saved {added_count} interactable(s) to {self.current_level_path}")
            return True
            
        except Exception as e:
            print(f"Error saving interactables to level file: {e}")
            return False
    
    def save_door_to_level_file(self, x: int, y: int, tile_id: str = "25") -> bool:
        """Save a door directly to the level JSON file"""
        if not self.current_level_path:
            print("No current level path set!")
            return False
        
        try:
            # Load the current level file
            with open(self.current_level_path, 'r') as f:
                level_data = json.load(f)
            
            # Find or create the interactables layer - handle multiple interactables layers
            interactables_layer = None
            duplicate_layers = []
            
            for i, layer in enumerate(level_data.get("layers", [])):
                if layer.get("name") == "interactables":
                    if interactables_layer is None:
                        interactables_layer = layer
                        print(f"Found primary interactables layer at index {i}")
                    else:
                        duplicate_layers.append((i, layer))
                        print(f"Found duplicate interactables layer at index {i}")
            
            # If there are duplicate layers, merge them into the first one
            if duplicate_layers:
                print(f"Merging {len(duplicate_layers)} duplicate interactables layers into primary layer")
                for layer_index, duplicate_layer in duplicate_layers:
                    # Add tiles from duplicate layer to primary layer
                    for tile in duplicate_layer.get("tiles", []):
                        interactables_layer["tiles"].append(tile)
                
                # Remove duplicate layers (in reverse order to maintain indices)
                for layer_index, _ in reversed(duplicate_layers):
                    del level_data["layers"][layer_index]
                    print(f"Removed duplicate interactables layer at index {layer_index}")
            
            if not interactables_layer:
                # Create new interactables layer
                interactables_layer = {
                    "name": "interactables",
                    "tiles": [],
                    "collider": False
                }
                level_data["layers"].append(interactables_layer)
                print("Created new interactables layer")
            
            # Check if a door already exists at this position
            for tile in interactables_layer["tiles"]:
                if tile["x"] == x and tile["y"] == y:
                    print(f"Door already exists at ({x}, {y})")
                    return False
            
            # Add new door (without required_rules - let system determine from rule_count)
            new_door = {
                "x": x,
                "y": y,
                "type": "door",
                "id": tile_id
            }
            
            interactables_layer["tiles"].append(new_door)
            
            # Save the modified level file
            with open(self.current_level_path, 'w') as f:
                json.dump(level_data, f, indent=2)
            
            print(f"Successfully saved door to {self.current_level_path} at ({x}, {y})")
            return True
            
        except Exception as e:
            print(f"Error saving door to level file: {e}")
            return False
    
    def _group_adjacent_tiles_static(self, tiles: Set[Tuple[int, int]]) -> List[Set[Tuple[int, int]]]:
        """Static version of tile grouping for saving to JSON"""
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
    
    def _detect_level_type(self, level_data: Dict[str, Any]) -> str:
        """
        Detect the type of level to determine rule loading strategy
        
        TODO: Extend this method to detect different level types
        """
        metadata = level_data.get("metadata", {})
        
        # Check if this is the tutorial level
        if metadata.get("description", "").lower().find("tutorial") != -1:
            return "tutorial"
        elif metadata.get("description", "").lower().find("test") != -1:
            return "tutorial"  # Test level uses tutorial rules
        
        # TODO: Add detection for other level types
        # elif metadata.get("difficulty") == "easy":
        #     return "easy_randomized"
        # elif metadata.get("difficulty") == "medium":
        #     return "medium_randomized"
        # elif metadata.get("difficulty") == "hard":
        #     return "hard_randomized"
        
        return "tutorial"  # Default to tutorial for now
    
    def _get_rules_for_level_type(self, level_type: str) -> List[str]:
        """
        Get the appropriate rules based on level type
        
        TODO: Implement randomization for different level types
        """
        rule_manager = game_state.rule_manager
        
        if level_type == "tutorial":
            return rule_manager.get_tutorial_rules()
        
        # TODO: Implement randomized rule selection for other level types
        # elif level_type == "easy_randomized":
        #     return rule_manager.get_randomized_rules(count=3)
        # elif level_type == "medium_randomized":
        #     return rule_manager.get_randomized_rules(count=5)
        # elif level_type == "hard_randomized":
        #     return rule_manager.get_randomized_rules(count=7)
        
        return rule_manager.get_tutorial_rules()  # Default fallback
        
    def _create_interactable(self, tile_data: Dict[str, Any], level_type: str) -> Interactable:
        """Create an interactable object from tile data"""
        x = tile_data.get("x", 0)
        y = tile_data.get("y", 0)
        tile_id = tile_data.get("id", "")  # Default to empty string if no id
        obj_type = tile_data.get("type", "")
        
        if obj_type == "note":
            rule = tile_data.get("rule", "")
            return Note(x, y, tile_id, rule)
        elif obj_type == "empty":
            return EmptyInteractable(x, y, tile_id)
        elif obj_type == "multi_note":
            # Multi-tile note
            coordinates = tile_data.get("coordinates", [])
            rule = tile_data.get("rule", "")
            if coordinates:
                # Convert coordinate format if needed
                tiles = set()
                for coord in coordinates:
                    if isinstance(coord, list) and len(coord) == 2:
                        tiles.add((coord[0], coord[1]))
                    elif isinstance(coord, tuple) and len(coord) == 2:
                        tiles.add(coord)
                if tiles:
                    return MultiTileNote(tiles, tile_id, rule)
        elif obj_type == "multi_empty":
            # Multi-tile empty interactable
            coordinates = tile_data.get("coordinates", [])
            if coordinates:
                # Convert coordinate format if needed
                tiles = set()
                for coord in coordinates:
                    if isinstance(coord, list) and len(coord) == 2:
                        tiles.add((coord[0], coord[1]))
                    elif isinstance(coord, tuple) and len(coord) == 2:
                        tiles.add(coord)
                if tiles:
                    return MultiTileEmptyInteractable(tiles, tile_id)
        elif obj_type == "door":
            # Use level's rule_count if available, otherwise use the door's specified required_rules
            if "rule_count" in self.level_metadata:
                required_rules = self.level_metadata["rule_count"]
            else:
                required_rules = tile_data.get("required_rules", 4)
            
            # Get next_level parameter for level transitions
            next_level = tile_data.get("next_level", None)
            
            door = Door(x, y, tile_id, required_rules, next_level)
            door.set_level_metadata(self.level_metadata)
            return door
        
        return None
    
    def get_interactable_at(self, x: int, y: int) -> Optional[Interactable]:
        """Get interactable object at given coordinates"""
        for obj in self.interactables:
            if obj.contains_tile(x, y):
                return obj
        return None
    
    def interact_at(self, x: int, y: int, player_x: int, player_y: int) -> Dict[str, Any]:
        """Interact with object at given coordinates"""
        obj = self.get_interactable_at(x, y)
        if obj:
            return obj.interact(player_x, player_y)
        return {"type": "none"}
    
    def add_multi_tile_interactable(self, tiles: Set[Tuple[int, int]], rule: str, tile_id: str = "25") -> MultiTileNote:
        """Add a new multi-tile interactable"""
        if not tiles:
            return None
        
        # Remove any existing interactables that overlap with these tiles
        self.interactables = [
            obj for obj in self.interactables 
            if not any(obj.contains_tile(x, y) for x, y in tiles)
        ]
        
        # Create new multi-tile note
        multi_note = MultiTileNote(tiles, tile_id, rule)
        self.interactables.append(multi_note)
        return multi_note
    
    def get_all_interactable_tiles(self) -> Set[Tuple[int, int]]:
        """Get all tile coordinates that contain interactables"""
        all_tiles = set()
        for obj in self.interactables:
            if isinstance(obj, MultiTileInteractable):
                all_tiles.update(obj.tiles)
            else:
                all_tiles.add((obj.x, obj.y))
        return all_tiles
    
    def add_interactable_coordinates(self, level_name: str, interactable_type: str, coordinates: List[Tuple[int, int]], rule: str = "", tile_id: str = "25"):
        """Add interactable coordinates for a specific level"""
        if level_name not in self.programmatic_interactables:
            self.programmatic_interactables[level_name] = []
        
        self.programmatic_interactables[level_name].append({
            "type": interactable_type,
            "coordinates": coordinates,
            "rule": rule,
            "tile_id": tile_id
        })
    
    def add_single_tile_interactable(self, level_name: str, x: int, y: int, rule: str, tile_id: str = "25"):
        """Add a single tile interactable at specific coordinates"""
        self.add_interactable_coordinates(level_name, "note", [(x, y)], rule, tile_id)
    
    def add_multi_tile_interactable_coords(self, level_name: str, coordinates: List[Tuple[int, int]], rule: str, tile_id: str = "25"):
        """Add a multi-tile interactable at specific coordinates"""
        self.add_interactable_coordinates(level_name, "multi_note", coordinates, rule, tile_id)
    
    def add_door_coordinates(self, level_name: str, x: int, y: int, required_rules: int = 4, tile_id: str = "13"):
        """Add a door at specific coordinates"""
        if level_name not in self.programmatic_interactables:
            self.programmatic_interactables[level_name] = []
        
        self.programmatic_interactables[level_name].append({
            "type": "door",
            "coordinates": [(x, y)],
            "required_rules": required_rules,
            "tile_id": tile_id
        })
    
    def _create_programmatic_interactable(self, interactable_def: Dict[str, Any]) -> Optional[Interactable]:
        """Create an interactable from programmatic definition"""
        obj_type = interactable_def.get("type", "")
        coordinates = interactable_def.get("coordinates", [])
        tile_id = interactable_def.get("tile_id", "25")
        
        if not coordinates:
            return None
        
        if obj_type == "note" and len(coordinates) == 1:
            # Single tile note
            x, y = coordinates[0]
            rule = interactable_def.get("rule", f"Rule at ({x}, {y})")
            return Note(x, y, tile_id, rule)
        
        elif obj_type == "multi_note" and len(coordinates) > 1:
            # Multi-tile note
            tiles = set(coordinates)
            rule = interactable_def.get("rule", f"Multi-tile rule covering {len(tiles)} tiles")
            return MultiTileNote(tiles, tile_id, rule)
        
        elif obj_type == "door" and len(coordinates) == 1:
            # Door
            x, y = coordinates[0]
            required_rules = interactable_def.get("required_rules", 4)
            next_level = interactable_def.get("next_level", None)
            door = Door(x, y, tile_id, required_rules, next_level)
            door.set_level_metadata(self.level_metadata)
            return door
        
        return None
    
    def setup_default_interactables(self):
        """Setup default interactables for various levels"""
        # Example interactables for level-1
        self.add_single_tile_interactable("level-1", 10, 5, "Password must be at least 8 characters long")
        self.add_single_tile_interactable("level-1", 15, 8, "Password must contain at least one number")
        self.add_single_tile_interactable("level-1", 20, 12, "Password must contain at least one uppercase letter")
        self.add_single_tile_interactable("level-1", 25, 15, "Password must end with a special character (!@#$%)")
        self.add_door_coordinates("level-1", 30, 10, required_rules=4)
        
        # Example multi-tile interactable for level-2
        self.add_multi_tile_interactable_coords("level-2", [(5, 5), (6, 5), (7, 5)], "This is a horizontal multi-tile rule")
        self.add_multi_tile_interactable_coords("level-2", [(10, 8), (10, 9), (11, 8), (11, 9)], "This is a 2x2 block rule")
        
        # Example for test-door-logic level
        self.add_single_tile_interactable("test-door-logic", 3, 3, "Additional rule: Password must not contain common words")
    
    def clear_programmatic_interactables(self, level_name: str = None):
        """Clear programmatically defined interactables"""
        if level_name:
            if level_name in self.programmatic_interactables:
                del self.programmatic_interactables[level_name]
        else:
            self.programmatic_interactables.clear()
    
    def list_programmatic_interactables(self, level_name: str = None) -> Dict[str, List]:
        """List all programmatically defined interactables"""
        if level_name:
            return {level_name: self.programmatic_interactables.get(level_name, [])}
        return self.programmatic_interactables.copy()

    def get_current_level_rules(self) -> List[str]:
        """Get the rules that were selected for the current level"""
        return self.level_metadata.get("rules", [])

    def clean_duplicate_interactables(self) -> bool:
        """Clean up duplicate interactables from the current level file"""
        if not self.current_level_path:
            print("Error: No current level path set")
            return False
        
        try:
            # Read current level data
            with open(self.current_level_path, 'r') as f:
                level_data = json.load(f)
            
            # Find interactables layer
            interactables_layer = None
            for layer in level_data.get("layers", []):
                if layer.get("name") == "interactables":
                    interactables_layer = layer
                    break
            
            if not interactables_layer:
                print("No interactables layer found")
                return False
            
            # Track unique coordinates and remove duplicates
            seen_coordinates = set()
            unique_tiles = []
            duplicates_removed = 0
            
            for tile in interactables_layer["tiles"]:
                coord = (tile["x"], tile["y"])
                if coord not in seen_coordinates:
                    seen_coordinates.add(coord)
                    unique_tiles.append(tile)
                else:
                    duplicates_removed += 1
            
            # Update the layer with unique tiles only
            interactables_layer["tiles"] = unique_tiles
            
            # Save back to file
            with open(self.current_level_path, 'w') as f:
                json.dump(level_data, f, indent=2)
            
            print(f"Cleaned up {duplicates_removed} duplicate interactables from {self.current_level_path}")
            return True
            
        except Exception as e:
            print(f"Error cleaning duplicate interactables: {e}")
            return False

    def delete_interactable_at_position(self, x: int, y: int) -> bool:
        """Delete an interactable at the specified position from the level JSON file"""
        if not self.current_level_path:
            print("Error: No current level path set")
            return False
        
        try:
            # Read current level data
            with open(self.current_level_path, 'r') as f:
                level_data = json.load(f)
            
            # Find interactables layer
            interactables_layer = None
            for layer in level_data.get("layers", []):
                if layer.get("name") == "interactables":
                    interactables_layer = layer
                    break
            
            if not interactables_layer:
                print("No interactables layer found")
                return False
            
            # Find and remove interactables at the specified position
            original_count = len(interactables_layer["tiles"])
            interactables_layer["tiles"] = [
                tile for tile in interactables_layer["tiles"] 
                if not (tile["x"] == x and tile["y"] == y)
            ]
            
            removed_count = original_count - len(interactables_layer["tiles"])
            
            if removed_count > 0:
                # Save back to file
                with open(self.current_level_path, 'w') as f:
                    json.dump(level_data, f, indent=2)
                
                print(f"Deleted {removed_count} interactable(s) at position ({x}, {y})")
                return True
            else:
                print(f"No interactables found at position ({x}, {y})")
                return False
            
        except Exception as e:
            print(f"Error deleting interactable: {e}")
            return False

    def _randomly_assign_rules_for_level(self):
        """Randomly assign rules to empty interactables in memory only (not saved to JSON)"""
        # Get all the rules that were selected for this level
        level_rules = self.level_metadata.get("rules", [])
        if not level_rules:
            # Fallback to tutorial rules if no level rules available
            level_rules = game_state.rule_manager.get_tutorial_rules()
        
        # Find all empty interactables in memory
        empty_interactables = [
            obj for obj in self.interactables 
            if isinstance(obj, (EmptyInteractable, MultiTileEmptyInteractable))
        ]
        
        if not empty_interactables:
            print("No empty interactables found in memory")
            return
        
        # Assign rules to interactables (up to the number of available empty interactables)
        num_rules_to_assign = min(len(level_rules), len(empty_interactables))
        
        # Randomly select which interactables get rules
        selected_interactables = random.sample(empty_interactables, num_rules_to_assign)
        
        # Convert selected empty interactables to note interactables with rules
        for i, (interactable, rule) in enumerate(zip(selected_interactables, level_rules[:num_rules_to_assign])):
            # Remove the old empty interactable
            self.interactables.remove(interactable)
            
            # Create new note interactable with the rule
            if isinstance(interactable, MultiTileEmptyInteractable):
                # Multi-tile note
                new_interactable = MultiTileNote(interactable.tiles, interactable.tile_id, rule)
            else:
                # Single tile note
                new_interactable = Note(interactable.x, interactable.y, interactable.tile_id, rule)
            
            # Add the new note interactable
            self.interactables.append(new_interactable)
            
            print(f"Assigned rule {i+1}/{num_rules_to_assign} to ({interactable.x}, {interactable.y}): {rule}")
        
        print(f"Successfully assigned {num_rules_to_assign} rules to {num_rules_to_assign} interactables (in memory only)")
        
        # Clear game state to remove any old rules before starting fresh
        game_state.clear_rules_for_testing()

    def assign_predetermined_rules(self, level_name: str, predetermined_rules: List[str]):
        """Assign predetermined rules to existing empty interactables in the level file"""
        if not self.current_level_path:
            print("Error: No current level path set")
            return False
        
        try:
            # Read current level data
            with open(self.current_level_path, 'r') as f:
                level_data = json.load(f)
            
            # Find interactables layer
            interactables_layer = None
            for layer in level_data.get("layers", []):
                if layer.get("name") == "interactables":
                    interactables_layer = layer
                    break
            
            if not interactables_layer:
                print("No interactables layer found")
                return False
            
            # Find empty interactables in the JSON
            empty_tiles = []
            for tile in interactables_layer["tiles"]:
                if tile.get("type") in ["empty", "multi_empty"]:
                    empty_tiles.append(tile)
            
            if not empty_tiles:
                print("No empty interactables found in level JSON")
                return False
            
            # Randomly select which empty interactables get the predetermined rules
            num_rules_to_assign = min(len(predetermined_rules), len(empty_tiles))
            selected_tiles = random.sample(empty_tiles, num_rules_to_assign)
            
            # Assign the predetermined rules
            for i, (tile, rule) in enumerate(zip(selected_tiles, predetermined_rules[:num_rules_to_assign])):
                # Convert empty to note with the predetermined rule
                if tile.get("type") == "multi_empty":
                    tile["type"] = "multi_note"
                else:
                    tile["type"] = "note"
                
                tile["rule"] = rule
                print(f"Assigned predetermined rule {i+1}/{num_rules_to_assign} to ({tile['x']}, {tile['y']}): {rule}")
            
            # Add rule_count to level metadata
            if "metadata" not in level_data:
                level_data["metadata"] = {}
            level_data["metadata"]["rule_count"] = len(predetermined_rules)
            
            # Save back to file
            with open(self.current_level_path, 'w') as f:
                json.dump(level_data, f, indent=2)
            
            print(f"Successfully assigned {num_rules_to_assign} predetermined rules to level {level_name}")
            print(f"Added rule_count: {len(predetermined_rules)} to level metadata")
            return True
            
        except Exception as e:
            print(f"Error assigning predetermined rules: {e}")
            return False

# Global interactable manager instance
interactable_manager = InteractableManager()

import pygame
import sys
import os
from typing import Dict, Any, Optional, Callable, List

# Add the src directory to the path so we can import game_state
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game_state import game_state

class Interactable:
    """Base class for interactable objects"""
    
    def __init__(self, x: int, y: int, tile_id: str, data: Dict[str, Any] = None):
        self.x = x
        self.y = y
        self.tile_id = tile_id
        self.data = data or {}
        self.active = True
        
    def interact(self, player_x: int, player_y: int) -> Dict[str, Any]:
        """Handle interaction with this object"""
        return {"type": "none", "message": "Nothing happens"}
    
    def is_near_player(self, player_x: int, player_y: int, distance: int = 20) -> bool:
        """Check if player is close enough to interact"""
        dx = abs(self.x - player_x)
        dy = abs(self.y - player_y)
        return dx <= distance and dy <= distance

class Note(Interactable):
    """A note containing a password rule"""
    
    def __init__(self, x: int, y: int, tile_id: str, rule: str, note_id: str = None):
        super().__init__(x, y, tile_id)
        self.rule = rule
        self.note_id = note_id or f"note_{x}_{y}"
        self.collected = False
        
    def interact(self, player_x: int, player_y: int) -> Dict[str, Any]:
        """Collect the note and add rule to game state"""
        if not self.collected and not game_state.has_note(self.note_id):
            self.collected = True
            game_state.add_rule(self.rule, self.note_id)
            return {
                "type": "note_collected",
                "message": f"Rule discovered: {self.rule}",
                "rule": self.rule,
                "total_rules": game_state.get_rules_count()
            }
        else:
            return {
                "type": "note_already_collected",
                "message": "You've already read this note.",
                "rule": self.rule
            }

class Door(Interactable):
    """A door that requires password validation"""
    
    def __init__(self, x: int, y: int, tile_id: str, required_rules: int = 4):
        super().__init__(x, y, tile_id)
        self.required_rules = required_rules
        self.is_open = False
        self.level_metadata = None
        
    def interact(self, player_x: int, player_y: int) -> Dict[str, Any]:
        """Handle door interaction - always show password prompt"""
        if self.is_open:
            return {
                "type": "door_open",
                "message": "The door is already open. You can pass through."
            }
        
        # Always show password prompt, but with missing rules as "????"
        all_rules = self._get_all_rules()
        collected_rules = game_state.get_rules()
        
        # Create rules list with "????" for missing rules
        display_rules = []
        for rule in all_rules:
            if rule in collected_rules:
                display_rules.append(rule)
            else:
                display_rules.append("????")
        
        rules_count = game_state.get_rules_count()
        if rules_count < self.required_rules:
            message = f"Enter password (you have {rules_count}/{self.required_rules} rules):"
        else:
            message = "You have all the rules! Enter the password:"
        
        return {
            "type": "door_password_prompt",
            "message": message,
            "rules": display_rules,
            "collected_rules": collected_rules,
            "door": self
        }
    
    def _get_all_rules(self) -> List[str]:
        """Get all possible rules from level metadata"""
        if self.level_metadata and "rules" in self.level_metadata:
            return self.level_metadata["rules"]
        # Fallback to default rules if metadata not available
        return [
            "Password must be at least 8 characters long",
            "Password must contain at least one number", 
            "Password must contain at least one uppercase letter",
            "Password must end with a special character (!@#$%)"
        ]
    
    def set_level_metadata(self, metadata: Dict[str, Any]):
        """Set level metadata for rule lookup"""
        self.level_metadata = metadata
    
    def try_password(self, password: str) -> Dict[str, Any]:
        """Try to open the door with a password"""
        validation_results = game_state.validate_password(password)
        is_valid = game_state.is_password_valid(password)
        
        if is_valid:
            self.is_open = True
            return {
                "type": "door_opened",
                "message": "Correct! The door opens.",
                "success": True,
                "validation_results": validation_results
            }
        else:
            return {
                "type": "door_failed",
                "message": "Incorrect password. Check the rules again.",
                "success": False,
                "validation_results": validation_results
            }

class InteractableManager:
    """Manages all interactable objects in a level"""
    
    def __init__(self):
        self.interactables: Dict[str, Interactable] = {}
        self.interaction_callback: Optional[Callable] = None
        self.level_metadata = None
        
    def set_interaction_callback(self, callback: Callable):
        """Set callback function for handling interaction results"""
        self.interaction_callback = callback
        
    def add_interactable(self, interactable: Interactable):
        """Add an interactable object"""
        key = f"{interactable.x}_{interactable.y}"
        self.interactables[key] = interactable
        
    def load_from_level_data(self, level_data: Dict[str, Any]):
        """Load interactables from level data"""
        self.clear()
        
        # Store level metadata
        self.level_metadata = level_data.get("metadata", {})
        
        for layer in level_data.get("layers", []):
            if layer.get("name") == "interactables":
                for tile in layer.get("tiles", []):
                    x = tile["x"] * level_data.get("tileSize", 16)
                    y = tile["y"] * level_data.get("tileSize", 16)
                    tile_id = tile["id"]
                    
                    # Create appropriate interactable based on tile data
                    if tile.get("type") == "note":
                        rule = tile.get("rule", "Unknown rule")
                        note_id = f"note_{tile['x']}_{tile['y']}"
                        note = Note(x, y, tile_id, rule, note_id)
                        self.add_interactable(note)
                        
                    elif tile.get("type") == "door":
                        required_rules = tile.get("requires_rules", 4)
                        door = Door(x, y, tile_id, required_rules)
                        door.set_level_metadata(self.level_metadata)
                        self.add_interactable(door)
    
    def check_interactions(self, player_x: int, player_y: int) -> Optional[Dict[str, Any]]:
        """Check for possible interactions near the player"""
        for interactable in self.interactables.values():
            if interactable.is_near_player(player_x, player_y):
                return {
                    "interactable": interactable,
                    "can_interact": True,
                    "type": type(interactable).__name__.lower()
                }
        return None
    
    def interact_with_nearest(self, player_x: int, player_y: int) -> Optional[Dict[str, Any]]:
        """Interact with the nearest interactable object"""
        nearest = None
        nearest_distance = float('inf')
        
        for interactable in self.interactables.values():
            if interactable.is_near_player(player_x, player_y):
                distance = ((interactable.x - player_x) ** 2 + (interactable.y - player_y) ** 2) ** 0.5
                if distance < nearest_distance:
                    nearest = interactable
                    nearest_distance = distance
        
        if nearest:
            result = nearest.interact(player_x, player_y)
            return result
        
        return None
    
    def clear(self):
        """Clear all interactables"""
        self.interactables.clear()
    
    def get_interactable_at(self, x: int, y: int) -> Optional[Interactable]:
        """Get interactable at specific coordinates"""
        key = f"{x}_{y}"
        return self.interactables.get(key)

# Global interactable manager instance
interactable_manager = InteractableManager()

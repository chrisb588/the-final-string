import pygame
import sys
import os
from typing import Dict, Any, Optional, Callable, List

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
        
        # Always show password prompt, but include info about missing rules
        collected_count = game_state.get_rules_count()
        collected_rules = game_state.get_rules()
        
        # Get all rules for this level from metadata
        all_rules = []
        if self.level_metadata and "rules" in self.level_metadata:
            all_rules = self.level_metadata["rules"]
        
        # Create display rules (show "????" for missing rules)
        display_rules = []
        for i, rule in enumerate(all_rules):
            if i < len(collected_rules):
                display_rules.append(collected_rules[i])
            else:
                display_rules.append("????")
        
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
                "message": "Password doesn't meet all the requirements.",
                "success": False,
                "validation_results": validation_results
            }

class InteractableManager:
    """Manages all interactable objects in a level"""
    
    def __init__(self):
        self.interactables: List[Interactable] = []
        self.level_metadata = None
        
    def load_from_level_data(self, level_data: Dict[str, Any]):
        """Load interactables from level data"""
        self.interactables.clear()
        self.level_metadata = level_data.get("metadata", {})
        
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
        tile_id = tile_data.get("id", "")
        obj_type = tile_data.get("type", "")
        
        if obj_type == "note":
            rule = tile_data.get("rule", "")
            return Note(x, y, tile_id, rule)
        elif obj_type == "door":
            required_rules = tile_data.get("requires_rules", 4)
            door = Door(x, y, tile_id, required_rules)
            door.set_level_metadata(self.level_metadata)
            return door
        
        return None
    
    def get_interactable_at(self, x: int, y: int) -> Interactable:
        """Get interactable object at given coordinates"""
        for obj in self.interactables:
            if obj.x == x and obj.y == y:
                return obj
        return None
    
    def interact_at(self, x: int, y: int, player_x: int, player_y: int) -> Dict[str, Any]:
        """Interact with object at given coordinates"""
        obj = self.get_interactable_at(x, y)
        if obj:
            return obj.interact(player_x, player_y)
        return {"type": "none"}

# Global interactable manager instance
interactable_manager = InteractableManager()

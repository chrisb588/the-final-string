"""
Interactable Configuration File

This file contains coordinate definitions for interactable objects in different levels.
You can easily modify coordinates and rules here without touching the main game code.
"""

from typing import List, Tuple, Dict, Any
from entities.interactables import interactable_manager

def setup_level_interactables():
    """Setup all interactable coordinates for different levels"""
    
    # Clear any existing programmatic interactables
    interactable_manager.clear_programmatic_interactables()
    
    # ===== LEVEL 1 INTERACTABLES =====
    setup_level_1()
    
    # ===== LEVEL 2 INTERACTABLES =====
    setup_level_2()
    
    # ===== LEVEL 3 INTERACTABLES =====
    setup_level_3()
    
    # ===== LEVEL 4 INTERACTABLES =====
    setup_level_4()
    
    # ===== TEST LEVEL INTERACTABLES =====
    setup_test_level()

def setup_level_1():
    """Setup interactables for Level 1"""
    level_name = "level-1"
    
    # Single tile notes with password rules
    interactable_manager.add_single_tile_interactable(
        level_name, 10, 5, 
        "Password must be at least 8 characters long"
    )
    
    interactable_manager.add_single_tile_interactable(
        level_name, 15, 8, 
        "Password must contain at least one number"
    )
    
    interactable_manager.add_single_tile_interactable(
        level_name, 20, 12, 
        "Password must contain at least one uppercase letter"
    )
    
    interactable_manager.add_single_tile_interactable(
        level_name, 25, 15, 
        "Password must end with a special character (!@#$%)"
    )
    
    # Door that requires all 4 rules
    interactable_manager.add_door_coordinates(
        level_name, 30, 10, 
        required_rules=4
    )

def setup_level_2():
    """Setup interactables for Level 2"""
    level_name = "level-2"
    
    # Multi-tile horizontal rule
    interactable_manager.add_multi_tile_interactable_coords(
        level_name, 
        [(5, 5), (6, 5), (7, 5)], 
        "Password must not contain your username"
    )
    
    # Multi-tile 2x2 block rule
    interactable_manager.add_multi_tile_interactable_coords(
        level_name, 
        [(10, 8), (10, 9), (11, 8), (11, 9)], 
        "Password must contain at least one lowercase letter"
    )
    
    # L-shaped multi-tile rule
    interactable_manager.add_multi_tile_interactable_coords(
        level_name, 
        [(15, 10), (15, 11), (15, 12), (16, 12), (17, 12)], 
        "Password must be different from your last 3 passwords"
    )
    
    # Single tile rule
    interactable_manager.add_single_tile_interactable(
        level_name, 20, 6, 
        "Password must not contain dictionary words"
    )
    
    # Door
    interactable_manager.add_door_coordinates(
        level_name, 25, 15, 
        required_rules=4
    )

def setup_level_3():
    """Setup interactables for Level 3"""
    level_name = "level-3"
    
    # Scattered single tiles
    # Multi-tile (add more coordinates):
    interactable_manager.add_multi_tile_interactable_coords(
        "level-3",
        [(132, 208), (130, 206), (130, 205), (130, 207), (131, 207), (132, 207), (133, 208)],
        "Testing"
    )
    
    interactable_manager.add_single_tile_interactable(
        level_name, 18, 8, 
        "Password must contain at least 2 numbers"
    )
    
    interactable_manager.add_single_tile_interactable(
        level_name, 25, 20, 
        "Password must contain at least 2 special characters"
    )
    
    # Vertical multi-tile rule
    interactable_manager.add_multi_tile_interactable_coords(
        level_name, 
        [(12, 5), (12, 6), (12, 7), (12, 8)], 
        "Password must not contain repeating characters"
    )
    
    # Door
    interactable_manager.add_door_coordinates(
        level_name, 30, 25, 
        required_rules=4
    )

def setup_level_4():
    """Setup interactables for Level 4"""
    level_name = "level-4"
    
    # Complex multi-tile patterns
    interactable_manager.add_multi_tile_interactable_coords(
        level_name, 
        [(5, 5), (6, 5), (7, 5), (6, 6), (6, 7)], 
        "Password must contain alternating letters and numbers"
    )
    
    interactable_manager.add_multi_tile_interactable_coords(
        level_name, 
        [(15, 10), (16, 10), (17, 10), (15, 11), (17, 11), (15, 12), (16, 12), (17, 12)], 
        "Password must start and end with the same character type"
    )
    
    # Single challenging rule
    interactable_manager.add_single_tile_interactable(
        level_name, 25, 8, 
        "Password must contain exactly 3 uppercase letters"
    )
    
    # Another single rule
    interactable_manager.add_single_tile_interactable(
        level_name, 10, 20, 
        "Password must not contain consecutive identical characters"
    )
    
    # Door with higher requirement
    interactable_manager.add_door_coordinates(
        level_name, 35, 15, 
        required_rules=4
    )

def setup_test_level():
    """Setup interactables for test-door-logic level"""
    level_name = "test-door-logic"
    
    # Additional rule that complements the existing ones in the JSON
    interactable_manager.add_single_tile_interactable(
        level_name, 3, 3, 
        "Password must not contain common words (password, 123456, etc.)"
    )
    
    # Multi-tile rule in corner
    interactable_manager.add_multi_tile_interactable_coords(
        level_name, 
        [(22, 2), (23, 2), (22, 3), (23, 3)], 
        "Password must contain mixed case letters"
    )

# ===== COORDINATE HELPER FUNCTIONS =====

def create_rectangle_coords(start_x: int, start_y: int, width: int, height: int) -> List[Tuple[int, int]]:
    """Create coordinates for a rectangular area"""
    coords = []
    for y in range(start_y, start_y + height):
        for x in range(start_x, start_x + width):
            coords.append((x, y))
    return coords

def create_line_coords(start_x: int, start_y: int, end_x: int, end_y: int) -> List[Tuple[int, int]]:
    """Create coordinates for a line (horizontal, vertical, or diagonal)"""
    coords = []
    
    # Calculate direction
    dx = 1 if end_x > start_x else -1 if end_x < start_x else 0
    dy = 1 if end_y > start_y else -1 if end_y < start_y else 0
    
    x, y = start_x, start_y
    while True:
        coords.append((x, y))
        if x == end_x and y == end_y:
            break
        x += dx
        y += dy
    
    return coords

def create_cross_coords(center_x: int, center_y: int, arm_length: int) -> List[Tuple[int, int]]:
    """Create coordinates for a cross/plus shape"""
    coords = [(center_x, center_y)]  # Center
    
    # Horizontal arm
    for i in range(1, arm_length + 1):
        coords.append((center_x - i, center_y))  # Left
        coords.append((center_x + i, center_y))  # Right
    
    # Vertical arm
    for i in range(1, arm_length + 1):
        coords.append((center_x, center_y - i))  # Up
        coords.append((center_x, center_y + i))  # Down
    
    return coords

# ===== EXAMPLE USAGE OF HELPER FUNCTIONS =====

def setup_example_patterns():
    """Example of using helper functions to create complex patterns"""
    level_name = "example-patterns"
    
    # Rectangle pattern
    rect_coords = create_rectangle_coords(10, 10, 3, 2)  # 3x2 rectangle
    interactable_manager.add_multi_tile_interactable_coords(
        level_name, rect_coords, 
        "Rectangle pattern rule"
    )
    
    # Line pattern
    line_coords = create_line_coords(5, 5, 5, 10)  # Vertical line
    interactable_manager.add_multi_tile_interactable_coords(
        level_name, line_coords, 
        "Line pattern rule"
    )
    
    # Cross pattern
    cross_coords = create_cross_coords(20, 15, 2)  # Cross with arm length 2
    interactable_manager.add_multi_tile_interactable_coords(
        level_name, cross_coords, 
        "Cross pattern rule"
    )

# Call this function to initialize all interactables
if __name__ == "__main__":
    setup_level_interactables()
    print("Interactable coordinates have been configured!") 
# Interactables Coordinate Guide

This guide explains how to add interactable objects (notes, doors, etc.) to your game levels using specific coordinates. **NEW: Interactables are now saved permanently to level JSON files!**

## Quick Start

1. **Run the game** and press `F3` to enable coordinate display
2. **Press `F4`** to enter creation mode
3. **Click tiles** to select them (yellow outline shows selection)
4. **Press `Enter`** to save the selected tiles as permanent interactables to the level JSON file
5. **Press `Z`** to randomize rules among all interactables in the level

## New Features

### 🔄 **Permanent Saving**
- Interactables are now saved directly to the level's JSON file
- No need to restart the game - changes are immediate
- Interactables persist between game sessions

### 🎲 **Rule Randomization**
- Create many interactables without rules (they'll show "nothing here")
- Press `Z` to randomly assign rules to ~30% of interactables
- Other interactables remain empty with random "nothing here" messages

### 📝 **Empty Interactables**
- Interactables without rules show messages like:
  - "There's nothing here."
  - "This spot seems empty."
  - "You find nothing of interest."

## Controls

| Key | Function |
|-----|----------|
| `F3` | Toggle coordinate display |
| `F4` | Toggle creation mode (for multi-tile selection) |
| `X` | Copy mouse coordinates to console (when coordinates shown) |
| `I` | Show interactables info for current level |
| `Z` | **NEW:** Randomize rules in current level |
| `Left Click` | Select tiles in creation mode / Interact with objects |
| `Enter` | **NEW:** Save interactables permanently to JSON file |

## Workflow for Creating Many Interactables

### Step 1: Create Empty Interactables
1. Press `F3` to show coordinates
2. Press `F4` to enter creation mode
3. Click on tiles where you want interactables (they'll have yellow outlines)
4. Press `Enter` to save them to the JSON file
5. Repeat for as many locations as you want

### Step 2: Randomize Rules
1. Once you have many empty interactables, press `Z`
2. The system will randomly assign rules to ~30% of your interactables
3. The rest will remain empty and show "nothing here" messages
4. You can press `Z` multiple times to get different randomizations

### Step 3: Fine-tune (Optional)
- Edit the level JSON file directly to assign specific rules to specific locations
- Or use the programmatic system in `interactable_config.py` for more control

## Example Workflow

```
1. Create 20 interactables around the level (all empty)
   - Press F4, click tiles, press Enter
   - Repeat until you have enough interactables

2. Randomize rules
   - Press Z to assign rules to ~6 of the 20 interactables
   - The other 14 will show "nothing here" when interacted with
```

## Rule Pool for Randomization

The system randomly selects from these rules:
- Password must be at least 8 characters long
- Password must contain at least one number
- Password must contain at least one uppercase letter
- Password must contain at least one lowercase letter
- Password must end with a special character (!@#$%)
- Password must not contain your username
- Password must not contain dictionary words
- Password must be different from your last 3 passwords
- Password must contain at least 2 numbers
- Password must contain at least 2 special characters
- Password must not contain repeating characters
- Password must contain alternating letters and numbers
- Password must start and end with the same character type
- Password must contain exactly 3 uppercase letters
- Password must not contain consecutive identical characters

## JSON File Structure

When you save interactables, they're added to the level's JSON file like this:

```json
{
  "layers": [
    {
      "name": "interactables",
      "tiles": [
        {
          "id": "25",
          "x": 10,
          "y": 5,
          "type": "empty"
        },
        {
          "id": "25", 
          "x": 15,
          "y": 8,
          "type": "note",
          "rule": "Password must be at least 8 characters long"
        }
      ],
      "collider": true
    }
  ]
}
```

## Advanced Features

### Multi-Tile Interactables
- Select adjacent tiles and they'll be grouped automatically
- Adjacent tiles become one interactable object
- Non-adjacent selections become separate interactables

### Visual Indicators
When coordinates are displayed (`F3`), you'll see:
- **Green outline**: Available interactables with rules
- **Gray outline**: Collected/used interactables  
- **Light gray outline**: Empty interactables (no rules)
- **Magenta outline**: Doors (locked)
- **Cyan outline**: Open doors
- **Yellow outline**: Selected tiles (creation mode)

## Tips for Level Design

1. **Create clusters**: Place interactables in logical groups around the level
2. **Mix empty and rule tiles**: Having many empty interactables makes finding rules more challenging
3. **Use the randomizer**: Press `Z` multiple times to find a good distribution
4. **Test frequently**: Walk around and interact to see how it feels
5. **Adjust percentage**: Edit the code to change the 30% rule assignment rate

## Troubleshooting

- **Changes not appearing**: Make sure you pressed `Enter` to save to JSON
- **Can't randomize**: Make sure there are interactables in the level first
- **File errors**: Check that the JSON file isn't corrupted
- **Wrong coordinates**: Use the `X` key to get accurate coordinates

## Coordinate System

- **Tile coordinates**: Each tile is 16x16 pixels
- **Origin (0,0)**: Top-left corner of the map
- **X increases**: Moving right
- **Y increases**: Moving down

## Legacy System

The old programmatic system in `interactable_config.py` still works for predefined setups, but the new JSON saving system is recommended for dynamic level creation.

## Types of Interactables

### 1. Single Tile Note
A note that occupies one tile and contains a password rule.

```python
interactable_manager.add_single_tile_interactable(
    "level-name", x, y, 
    "Your rule text here"
)
```

### 2. Multi-Tile Note
A note that spans multiple adjacent tiles, treated as one interactable object.

```python
interactable_manager.add_multi_tile_interactable_coords(
    "level-name", 
    [(x1, y1), (x2, y2), (x3, y3)], 
    "Your multi-tile rule text here"
)
```

### 3. Door
A door that requires a certain number of collected rules to open.

```python
interactable_manager.add_door_coordinates(
    "level-name", x, y, 
    required_rules=4
)
```

## Configuration File

All interactable coordinates are defined in `src/interactable_config.py`. This file contains:

- **Level-specific functions**: `setup_level_1()`, `setup_level_2()`, etc.
- **Helper functions**: For creating patterns like rectangles, lines, crosses
- **Main setup function**: `setup_level_interactables()` that calls all level functions

## Adding Interactables to a Level

### Method 1: Using the Game Interface

1. Load the level you want to modify
2. Press `F3` to show coordinates
3. Move mouse to desired location
4. Press `X` to get code examples
5. Copy the code to the appropriate level function in `interactable_config.py`

### Method 2: Direct Code Editing

Edit `src/interactable_config.py` and add your interactables to the appropriate level function:

```python
def setup_level_1():
    """Setup interactables for Level 1"""
    level_name = "level-1"
    
    # Add a single tile note
    interactable_manager.add_single_tile_interactable(
        level_name, 10, 5, 
        "Password must be at least 8 characters long"
    )
    
    # Add a door
    interactable_manager.add_door_coordinates(
        level_name, 30, 10, 
        required_rules=4
    )
```

## Helper Functions for Complex Patterns

### Rectangle Pattern
```python
from interactable_config import create_rectangle_coords

# Create a 3x2 rectangle starting at (10, 5)
coords = create_rectangle_coords(10, 5, 3, 2)
interactable_manager.add_multi_tile_interactable_coords(
    "level-name", coords, "Rectangle rule"
)
```

### Line Pattern
```python
from interactable_config import create_line_coords

# Create a line from (5, 5) to (5, 10)
coords = create_line_coords(5, 5, 5, 10)
interactable_manager.add_multi_tile_interactable_coords(
    "level-name", coords, "Line rule"
)
```

### Cross Pattern
```python
from interactable_config import create_cross_coords

# Create a cross centered at (15, 10) with arm length 2
coords = create_cross_coords(15, 10, 2)
interactable_manager.add_multi_tile_interactable_coords(
    "level-name", coords, "Cross rule"
)
```

## Visual Indicators

When coordinates are displayed (`F3`), you'll see:

- **Green outline**: Available interactables
- **Gray outline**: Collected/used interactables  
- **Magenta outline**: Doors (locked)
- **Cyan outline**: Open doors
- **Yellow outline**: Selected tiles (creation mode)

## Level Names

Make sure to use the correct level names when adding interactables:

- `"level-0"` - Tutorial level
- `"level-1"` - First main level
- `"level-2"` - Second main level
- `"level-3"` - Third main level
- `"level-4"` - Fourth main level
- `"test-door-logic"` - Test level

## Example: Adding a Complex Multi-Tile Rule

Let's say you want to add an L-shaped interactable to level-2:

1. **Find coordinates**: Use the game interface to find the coordinates
2. **Define the shape**: 
   ```python
   # L-shape coordinates
   l_shape_coords = [
       (15, 10), (15, 11), (15, 12),  # Vertical part
       (16, 12), (17, 12)             # Horizontal part
   ]
   ```
3. **Add to config**:
   ```python
   def setup_level_2():
       level_name = "level-2"
       
       # L-shaped multi-tile rule
       interactable_manager.add_multi_tile_interactable_coords(
           level_name, 
           [(15, 10), (15, 11), (15, 12), (16, 12), (17, 12)], 
           "Password must be different from your last 3 passwords"
       )
   ```

## Tips

1. **Test coordinates**: Use the coordinate display to verify positions
2. **Group related rules**: Place related password rules near each other
3. **Use patterns**: Multi-tile interactables can create interesting visual patterns
4. **Check for overlaps**: The system automatically removes overlapping interactables
5. **Restart to see changes**: You need to restart the game after modifying the config file

## Troubleshooting

- **Interactables not appearing**: Check that the level name matches exactly
- **Wrong coordinates**: Use the `X` key to get accurate coordinates
- **Overlapping issues**: The system removes old interactables when adding new ones at the same coordinates
- **Config not loading**: Make sure there are no syntax errors in `interactable_config.py`

## Advanced Usage

### Creating Custom Patterns

You can create your own helper functions for specific patterns:

```python
def create_spiral_coords(center_x, center_y, radius):
    """Create a spiral pattern"""
    coords = []
    # Your spiral logic here
    return coords

# Use it
spiral_coords = create_spiral_coords(20, 15, 3)
interactable_manager.add_multi_tile_interactable_coords(
    "level-name", spiral_coords, "Spiral rule"
)
```

### Dynamic Coordinate Generation

You can also generate coordinates programmatically:

```python
def setup_level_dynamic():
    level_name = "dynamic-level"
    
    # Create a grid of single-tile interactables
    for x in range(5, 20, 3):  # Every 3 tiles from x=5 to x=20
        for y in range(5, 15, 3):  # Every 3 tiles from y=5 to y=15
            interactable_manager.add_single_tile_interactable(
                level_name, x, y, 
                f"Rule at ({x}, {y})"
            )
``` 
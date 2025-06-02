# NPC System Usage Guide

## Overview
The NPC (Non-Player Character) system allows you to add interactive characters to your levels that can optionally provide password rules. NPCs behave similarly to notes but with personality and different interaction messages.

## NPC Features

### 🎭 **Available NPC Names**
- Resting Goblin
- Evil Chest
- Mushroom Guy
- Skelly Henchman
- Skelly Captain
- Guardian of the Agaricales
- Mr. Froggy
- Goblin Miner
- Alagad ni Colonel Sanders
- Moo-chan

### 🎮 **Interaction Behavior**

**NPCs WITH Rules:**
- First interaction: `"[NPC Name]: [custom message with rule]"`
- After giving rule: `"[NPC Name]: I already told you my secret!"`

**NPCs WITHOUT Rules:**
- Casual conversation: `"[NPC Name]: [custom casual message]"`

### 📝 **Two Ways to Add NPCs**

## Method 1: JSON Persistence (NEW!)

Save NPCs directly to level JSON files - these persist permanently and load automatically. **NPCs saved to JSON have no hard-coded rules and participate in rule randomization.**

### 🔧 **Creator Tool JSON Methods**

**Single-Tile NPCs:**
```python
# Set the level file to modify
interactable_manager.set_current_level_path("levels/my-level.json")

# Save NPC with specific name (rule will be randomized at runtime)
interactable_manager.save_npc_to_level_file(
    x=10, y=5,
    npc_name="Resting Goblin",
    tile_id="26"
)

# Save NPC with random name (rule will be randomized at runtime)
interactable_manager.save_npc_to_level_file(
    x=15, y=8,
    tile_id="27"
)
```

**Multi-Tile NPCs:**
```python
# Large NPC covering multiple tiles (rule will be randomized at runtime)
large_npc_coords = [(20, 5), (21, 5), (22, 5), (20, 6), (21, 6), (22, 6)]
interactable_manager.save_multi_tile_npc_to_level_file(
    coordinates=large_npc_coords,
    npc_name="Guardian of the Agaricales",
    tile_id="29"
)
```

**What Gets Saved to JSON:**
```json
{
  "layers": [
    {
      "name": "interactables",
      "tiles": [
        {
          "x": 10,
          "y": 5,
          "type": "npc",
          "npc_name": "Resting Goblin",
          "id": "26"
        },
        {
          "x": 20,
          "y": 5,
          "type": "multi_npc",
          "coordinates": [[20, 5], [21, 5], [22, 5], [20, 6], [21, 6], [22, 6]],
          "npc_name": "Guardian of the Agaricales",
          "id": "29"
        }
      ]
    }
  ]
}
```

**Note:** No `"rule"` field is saved! Rules are assigned randomly at runtime based on the level's `rule_count`.

## Method 2: Programmatic (Original)

Add NPCs via code - these are applied at runtime and don't persist in JSON files.

## Usage in Creator Tool

### 📍 **Single-Tile NPCs**

```python
# NPC with a specific rule
interactable_manager.add_single_tile_npc(
    level_name="my-level", 
    x=10, y=5, 
    npc_name="Resting Goblin", 
    rule="Password must contain the word 'goblin'",
    tile_id="26"
)

# NPC without rule (atmosphere only)
interactable_manager.add_single_tile_npc(
    level_name="my-level", 
    x=15, y=8, 
    npc_name="Moo-chan",
    tile_id="27"
)

# NPC with random name from the list
interactable_manager.add_single_tile_npc(
    level_name="my-level", 
    x=20, y=12, 
    rule="Password must end with '!'",
    tile_id="28"
)
```

### 🗺️ **Multi-Tile NPCs**

```python
# Large NPC covering multiple tiles
large_npc_coords = [(20, 5), (21, 5), (22, 5), (20, 6), (21, 6), (22, 6)]
interactable_manager.add_multi_tile_npc_coords(
    level_name="my-level", 
    coordinates=large_npc_coords,
    npc_name="Guardian of the Agaricales",
    rule="Password must contain a mushroom reference",
    tile_id="29"
)

# L-shaped NPC without rule
l_shape_coords = [(25, 10), (25, 11), (25, 12), (26, 12), (27, 12)]
interactable_manager.add_multi_tile_npc_coords(
    level_name="my-level", 
    coordinates=l_shape_coords,
    npc_name="Mr. Froggy",
    tile_id="30"
)
```

## Integration with Rule System

### 🎲 **Rule Randomization Support**
NPCs with rules participate in the extended rule randomization system just like notes:
- NPCs can receive randomized rules from the extended rules pool
- They count toward the total rule requirement for doors
- Mix NPCs and notes freely in your levels

### 🚪 **Door Integration**
```python
# Door that requires rules from both notes and NPCs
interactable_manager.add_door_coordinates(
    level_name="my-level", 
    x=30, y=15, 
    required_rules=4  # Can be satisfied by any combination of notes and NPCs
)
```

## Complete Level Example

```python
def setup_my_custom_level():
    """Example level with mixed NPCs and notes"""
    level_name = "custom-npc-level"
    
    # Traditional note
    interactable_manager.add_single_tile_interactable(
        level_name, 5, 5, 
        "Password must be at least 8 characters long"
    )
    
    # Rule-giving NPCs
    interactable_manager.add_single_tile_npc(
        level_name, 10, 8, 
        npc_name="Wise Goblin Miner", 
        rule="Password must contain at least one number"
    )
    
    interactable_manager.add_single_tile_npc(
        level_name, 15, 12, 
        npc_name="Skelly Captain",
        rule="Password must contain at least one uppercase letter"
    )
    
    # Atmospheric NPC (no rule)
    interactable_manager.add_single_tile_npc(
        level_name, 20, 6, 
        npc_name="Evil Chest"
    )
    
    # Multi-tile NPC with rule
    mushroom_coords = [(25, 10), (26, 10), (25, 11), (26, 11)]
    interactable_manager.add_multi_tile_npc_coords(
        level_name, mushroom_coords,
        npc_name="Guardian of the Agaricales",
        rule="Password must contain a special character (!@#$%)"
    )
    
    # Door requiring 4 rules total
    interactable_manager.add_door_coordinates(
        level_name, 30, 15, 
        required_rules=4
    )
```

## Best Practices

### 🎨 **Design Tips**
1. **Mix Rule Types**: Combine NPCs with rules, NPCs without rules, and traditional notes
2. **Use Appropriate Names**: Match NPC names to your level theme
3. **Vary Tile IDs**: Use different tile IDs for visual variety
4. **Strategic Placement**: Place important NPCs in memorable locations

### ⚖️ **Balance Considerations**
1. **Rule Distribution**: Not every NPC needs a rule - some can just add atmosphere
2. **Casual Conversation**: NPCs without rules provide world-building opportunities
3. **Multi-tile Usage**: Large NPCs work great for boss-like characters or important story elements

### 🔧 **Technical Notes**
1. **Random Names**: If you don't specify `npc_name`, one will be chosen randomly
2. **Rule Integration**: NPCs with rules work identically to notes in the validation system
3. **Tile Coverage**: Multi-tile NPCs can be interacted with at any of their tiles
4. **Performance**: NPCs have the same performance characteristics as notes

## Activation

To use NPCs in your levels, simply call the setup functions in your `interactable_config.py`:

```python
def setup_level_interactables():
    # ... existing setup code ...
    
    # Add your custom NPC level
    setup_my_custom_level()
```

The NPC system seamlessly integrates with the existing creator tool and rule randomization system! 

## 🚀 **Practical Usage Example**

Here's a complete example of using the new JSON persistence for NPCs:

```python
from entities.interactables import interactable_manager

def create_npc_level():
    """Example: Create a level with persistent NPCs using JSON saving"""
    
    # Set the level file to modify
    interactable_manager.set_current_level_path("levels/npc-village.json")
    
    # Add various NPCs (rules will be randomized at runtime)
    interactable_manager.save_npc_to_level_file(
        x=5, y=5,
        npc_name="Resting Goblin",
        tile_id="26"
    )
    
    interactable_manager.save_npc_to_level_file(
        x=10, y=8,
        npc_name="Evil Chest",
        tile_id="27"
    )
    
    # Add NPCs with random names (will be chosen from NPC_NAMES list)
    interactable_manager.save_npc_to_level_file(
        x=15, y=12,
        tile_id="28"
    )
    
    # Add a large multi-tile NPC
    guardian_coords = [(20, 5), (21, 5), (22, 5), (20, 6), (21, 6), (22, 6)]
    interactable_manager.save_multi_tile_npc_to_level_file(
        coordinates=guardian_coords,
        npc_name="Guardian of the Agaricales",
        tile_id="29"
    )
    
    # Add some empty interactables to compete for rules
    interactable_manager.save_interactables_to_level_file({(25, 10), (30, 12)})
    
    # Add door that requires rules from mixed sources
    interactable_manager.save_door_to_level_file(x=35, y=15, tile_id="13")
    
    print("✅ NPC village level created!")
    print("🎲 Rules will be randomly assigned to NPCs and empty spots at runtime")

# Run this to create your level
create_npc_level()
```

### 🎯 **Runtime Behavior:**

When the level loads with `rule_count=4`:
1. **4 NPCs** and **2 empty interactables** = **6 total candidates**
2. **Random selection**: 4 candidates get rules, 2 remain without rules
3. **Possible outcomes**:
   - 3 NPCs get rules + 1 empty spot gets rule
   - 2 NPCs get rules + 2 empty spots get rules  
   - 4 NPCs get rules + 0 empty spots get rules
   - etc.

**NPCs with rules**: Use custom character messages  
**NPCs without rules**: Show casual conversation messages

### 🔄 **Key Benefits of JSON Persistence:**

1. **Permanent Storage**: NPCs are saved directly in level files
2. **Automatic Loading**: No need for programmatic setup - they just appear
3. **Level Editor Friendly**: Works with visual level editing tools
4. **Mixed Usage**: Can combine JSON NPCs with programmatic ones
5. **Easy Management**: Use creator tool methods to add/remove NPCs

### 🆚 **JSON vs Programmatic Comparison:**

| Feature | JSON Persistence | Programmatic |
|---------|------------------|--------------|
| **Persistence** | ✅ Saved in level files | ❌ Runtime only |
| **Auto-loading** | ✅ Loads automatically | ❌ Needs code setup |
| **Level Editor** | ✅ Compatible | ⚠️ Code-based only |
| **Rule Management** | ✅ Stored with NPC | ✅ Stored in config |
| **Flexibility** | ⚠️ Manual editing | ✅ Dynamic generation |

**Recommendation**: Use **JSON Persistence** for designed levels, **Programmatic** for dynamic/generated content! 
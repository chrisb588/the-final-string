#!/usr/bin/env python3
"""
Script to add rule_count field to all level JSON files
"""

import json
import os

def add_rule_count_to_level(file_path, rule_count):
    """Add rule_count to a level JSON file"""
    try:
        with open(file_path, 'r') as f:
            level_data = json.load(f)
        
        # Add metadata if it doesn't exist
        if "metadata" not in level_data:
            level_data["metadata"] = {}
        
        # Add rule_count
        level_data["metadata"]["rule_count"] = rule_count
        
        # Save back to file
        with open(file_path, 'w') as f:
            json.dump(level_data, f, indent=2)
        
        print(f"✓ Added rule_count={rule_count} to {os.path.basename(file_path)}")
        return True
        
    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to process all level files"""
    level_files = {
        "src/levels/level-data/level-0.json": 4,  # Tutorial level with predetermined rules
        "src/levels/level-data/level-1.json": 4,  # Standard difficulty
        "src/levels/level-data/level-2.json": 5,  # Slightly harder
        "src/levels/level-data/level-3.json": 6,  # More challenging
        "src/levels/level-data/level-4.json": 7,  # Advanced level
        "src/levels/level-data/test-door-logic.json": 4,  # Test level
        "src/levels/level-data/test-randomization.json": 5,  # Test level
        "src/levels/level-data/example-with-starting-point.json": 3,  # Example level
    }
    
    print("Adding rule_count to level JSON files...")
    print("=" * 50)
    
    success_count = 0
    total_count = len(level_files)
    
    for file_path, rule_count in level_files.items():
        if os.path.exists(file_path):
            if add_rule_count_to_level(file_path, rule_count):
                success_count += 1
        else:
            print(f"✗ File not found: {file_path}")
    
    print("=" * 50)
    print(f"Successfully updated {success_count}/{total_count} files")
    
    if success_count == total_count:
        print("🎉 All files updated successfully!")
    else:
        print("⚠️ Some files failed to update")

if __name__ == "__main__":
    main() 
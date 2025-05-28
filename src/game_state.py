import re
from typing import List, Dict, Set
import random

class PasswordRuleManager:
    """Manages password rules with separation between tutorial and extended rules"""
    
    def __init__(self):
        # ========================================
        # TUTORIAL RULES (Level 1 - Fixed Set)
        # ========================================
        self.tutorial_rules = [
            "Password must be at least 8 characters long",
            "Password must contain at least one number", 
            "Password must contain at least one uppercase letter",
            "Password must end with a special character (!@#$%)"
        ]
        
        # ========================================
        # EXTENDED RULES (Future Levels - Add Here)
        # ========================================
        # TODO: Add more rules here for randomized selection in future levels
        # Example rules to implement:
        self.extended_rules = [
            # "Password must contain at least one lowercase letter",
            # "Password must not contain consecutive identical characters",
            # "Password must contain at least 2 special characters",
            # "Password must not contain your username",
            # "Password must contain at least one vowel",
            # "Password must not contain common words (password, 123456, etc.)",
            # "Password must have digits that sum to at least 15",
            # "Password must contain a month name",
            # "Password must include Roman numerals that add up to 35",
            # "Password must contain the current year",
            # "Password must include a country name",
            # "Password must contain an emoji",
            # "Password must be a palindrome",
            # "Password must contain prime numbers only",
            # "Password must include chess notation",
        ]
    
    def get_tutorial_rules(self) -> List[str]:
        """Get the fixed tutorial rules for level 1"""
        return self.tutorial_rules.copy()
    
    def get_randomized_rules(self, count: int = 4) -> List[str]:
        """
        Get randomized rules for future levels
        
        Args:
            count: Number of rules to select
            
        Returns:
            List of randomly selected rules
            
        TODO: Implement randomization logic here
        This is where you'll add the randomizer for future levels
        """
        # For now, return tutorial rules as placeholder
        # Future implementation should randomly select from extended_rules
        return self.tutorial_rules[:count]
    
    def validate_rule(self, password: str, rule: str) -> bool:
        """Validate password against a single rule"""
        rule_lower = rule.lower()
        
        # ========================================
        # TUTORIAL RULE VALIDATION
        # ========================================
        
        # Rule 1: Password must be at least 8 characters long
        if "at least 8 characters" in rule_lower:
            return len(password) >= 8
        
        # Rule 2: Password must contain at least one number
        elif "contain at least one number" in rule_lower:
            return any(char.isdigit() for char in password)
        
        # Rule 3: Password must contain at least one uppercase letter
        elif "contain at least one uppercase" in rule_lower:
            return any(char.isupper() for char in password)
        
        # Rule 4: Password must end with a special character
        elif "end with a special character" in rule_lower:
            special_chars = "!@#$%"
            return len(password) > 0 and password[-1] in special_chars
        
        # ========================================
        # EXTENDED RULE VALIDATION (Add Here)
        # ========================================
        # TODO: Add validation logic for extended rules here
        # Example implementations:
        
        # elif "contain at least one lowercase" in rule_lower:
        #     return any(char.islower() for char in password)
        
        # elif "not contain consecutive identical" in rule_lower:
        #     for i in range(len(password) - 1):
        #         if password[i] == password[i + 1]:
        #             return False
        #     return True
        
        # elif "contain at least 2 special characters" in rule_lower:
        #     special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        #     count = sum(1 for char in password if char in special_chars)
        #     return count >= 2
        
        # Default case - unknown rule
        return True

class GameState:
    """Manages the global game state including collected notes and password rules"""
    
    def __init__(self):
        self.collected_rules: List[str] = []
        self.collected_notes: Set[str] = set()  # Track which notes have been collected
        self.current_level = None
        self.rule_manager = PasswordRuleManager()
        
    def add_rule(self, rule: str, note_id: str = None):
        """Add a rule to the collected rules"""
        if rule not in self.collected_rules:
            self.collected_rules.append(rule)
            if note_id:
                self.collected_notes.add(note_id)
            print(f"Rule collected: {rule}")
    
    def has_rule(self, rule: str) -> bool:
        """Check if a specific rule has been collected"""
        return rule in self.collected_rules
    
    def has_note(self, note_id: str) -> bool:
        """Check if a specific note has been collected"""
        return note_id in self.collected_notes
    
    def get_rules_count(self) -> int:
        """Get the number of rules collected"""
        return len(self.collected_rules)
    
    def get_rules(self) -> List[str]:
        """Get all collected rules"""
        return self.collected_rules.copy()
    
    def validate_password(self, password: str) -> Dict[str, bool]:
        """Validate password against all collected rules"""
        results = {}
        
        for rule in self.collected_rules:
            results[rule] = self.rule_manager.validate_rule(password, rule)
        
        return results
    
    def validate_password_against_all_rules(self, password: str, all_rules: List[str]) -> Dict[str, bool]:
        """Validate password against all possible rules (including uncollected ones)"""
        results = {}
        
        for rule in all_rules:
            if rule == "????":
                # For missing rules, we can't validate so mark as False
                results[rule] = False
            else:
                results[rule] = self.rule_manager.validate_rule(password, rule)
        
        return results
    
    def _validate_single_rule(self, password: str, rule: str) -> bool:
        """Validate password against a single rule (deprecated - use rule_manager)"""
        return self.rule_manager.validate_rule(password, rule)
    
    def is_password_valid(self, password: str) -> bool:
        """Check if password satisfies all collected rules"""
        if not self.collected_rules:
            return False
        
        validation_results = self.validate_password(password)
        return all(validation_results.values())
    
    def reset_level_state(self):
        """Reset state for a new level (but keep collected rules)"""
        # Keep collected rules between levels
        pass
    
    def reset_game_state(self):
        """Reset all game state"""
        self.collected_rules.clear()
        self.collected_notes.clear()
        self.current_level = None
    
    def clear_rules_for_testing(self):
        """Clear collected rules for testing purposes"""
        self.collected_rules.clear()
        self.collected_notes.clear()

# Global game state instance
game_state = GameState() 
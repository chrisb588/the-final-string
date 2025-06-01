import re
from typing import List, Dict, Set
import random

class PasswordRuleManager:
    """Manages password rules with separation between tutorial and extended rules"""
    
    def __init__(self):
        # ========================================
        # TUTORIAL RULES (Level 0 - Fixed Set)
        # ========================================
        self.tutorial_rules = [
            "Password must be at least 8 characters long",
            "Password must contain at least one number", 
            "Password must contain at least one uppercase letter",
            "Password must contain a special character (!@#$%)"
        ]
        
        # ========================================
        # EXTENDED RULES (For Randomization - Add Here)
        # ========================================
        self.extended_rules = [
            "The length of your password must be an odd number.",
            "Your password must contain the '😎' emoji.",
            "Your password should contain the string 'This is the best game that has ever been made in the entire universe!.'",
            "Your password must contain a number that is a factor of 141.",
            "Your password must contain the answer to this question 'Who is in the Top 3 spot in the world in tennis men's singles category who has not won a single Grand Slam?'",
            "Your password must contain any of the words in the sixth line in the third verse of the hit song 'luther' by Kendrick Lamar & SZA found on the website for geniuses",
            "Your password must contain a palindrome that's exactly 7 characters long.",
            "Your password must begin with the final word ever spoken in The Lord of the Rings.",
            "Your password must contain the correct answer to this question: 'Fill in the blanks: CMSC 141 is the ___ course ever! 'best' or 'worst''",
            "Your password must contain the current level you are on in text form."
        ]
    
    def get_tutorial_rules(self) -> List[str]:
        """Get the fixed tutorial rules for level 1"""
        return self.tutorial_rules.copy()
    
    def get_randomized_rules(self, count: int = 4, exclude_rules: set = None) -> List[str]:
        """
        Get randomized rules for levels that use rule_count
        
        Args:
            count: Number of rules to select
            exclude_rules: Set of rules to exclude from selection
            
        Returns:
            List of randomly selected rules from extended_rules (excluding specified rules)
        """
        if exclude_rules is None:
            exclude_rules = set()
        
        # Filter out excluded rules
        available_rules = [rule for rule in self.extended_rules if rule not in exclude_rules]
        
        if count <= len(available_rules):
            return random.sample(available_rules, count)
        else:
            # If requesting more rules than available, return all available rules
            print(f"Warning: Requested {count} rules but only {len(available_rules)} available after exclusions")
            return available_rules.copy()
    
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
        
        # Rule 4: Password must contain a special character
        elif "contain a special character" in rule_lower:
            special_chars = "!@#$%"
            return len(password) > 0 and any(char in special_chars for char in password)
        
        # ========================================
        # EXTENDED RULE VALIDATION (Add Here)
        # ========================================
        
        # The length of your password must be an odd number
        elif "length of your password must be an odd number" in rule_lower:
            return len(password) % 2 == 1
        
        # Your password must contain the '😎' emoji
        elif "contain the '😎' emoji" in rule_lower or "'😎' emoji" in rule_lower or "😎" in rule:
            return "😎" in password
        
        # Your password should contain the string "This is the best game that has ever been made in the entire universe!"
        elif "this is the best game that has ever been made in the entire universe" in rule_lower:
            return "This is the best game that has ever been made in the entire universe!" in password
        
        # Your password must contain a number that is a factor of 141
        elif "factor of 141" in rule_lower:
            factors_141 = ["1", "3", "47", "141"]
            return any(factor in password for factor in factors_141)
        
        # Your password must contain "Alexander Zverev" (either "alexander" or "zverev" is acceptable)
        elif "alexander zverev" in rule_lower or "top 3 spot in the world in tennis" in rule_lower:
            password_lower = password.lower()
            return "alexander" in password_lower or "zverev" in password_lower
        
        # Your password must contain any of the words from Kendrick Lamar & SZA "luther" song
        elif "luther" in rule_lower and "kendrick lamar" in rule_lower:
            luther_words = ["I", "might", "even", "settle", "down", "for", "you", "I'ma", "show", "you", "I'm", "a", "pro"]
            return any(word in password for word in luther_words)
        
        # Your password must contain a palindrome that's exactly 7 characters long
        elif "palindrome that's exactly 7 characters long" in rule_lower:
            # Check for any 7-character palindrome in the password
            for i in range(len(password) - 6):  # -6 because we need 7 characters
                substring = password[i:i+7]
                # Check if this 7-character substring is a palindrome
                if substring.lower() == substring.lower()[::-1]:
                    return True
            return False
        
        # Your password must begin with "back" (final word from LOTR)
        elif "begin with the final word ever spoken in the lord of the rings" in rule_lower:
            return password.lower().startswith("back")
        
        # Your password must contain "best" (answer to CMSC 141 question)
        elif "cmsc 141 is the" in rule_lower and "course ever" in rule_lower:
            return "best" in password.lower()
        
        # Your password must contain the current level in text form
        elif "current level you are on in text form" in rule_lower:
            # This would need to be dynamically determined based on current level
            # For now, let's check for common level names
            level_names = ["level-0", "level-1", "level-2", "level-3", "level-4", "zero", "one", "two", "three", "four"]
            password_lower = password.lower()
            return any(level_name in password_lower for level_name in level_names)
        
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
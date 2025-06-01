import re
from typing import List, Dict, Set
import random
import datetime
import base64

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
            "Your password must contain the current level you are on in text form.",
            "Your password must contain the sum of the numbers of the current hour and day today mod 7.",
            "The digits of your password must sum up to a multiple of 141.",
            "Your password must contain one Japanese hiragana character.",
            "Your password must contain the 46th-50th decimal digits of pi.",
            "Your password must contain the first two words of Franz Kafka's novella 'The Metamorphosis'.",
            "Your password must contain an anagram of the word 'secure'.",
            "Add the reversed name of the inventor of the world's first computer program.",
            "Add the answer to this question to the password: 'From a finite alphabet Σ, how many strings can be made?'",
            "Your password must include a prime number sandwiched between two hash signs.",
            "From the grammar: S → aSb | ab. What are the only valid strings of length 4?",
            "Your password must contain a string in the language defined by the regular expression (a*(ab | bb)*) over the alphabet {a,b}.",
            "Include a base64-encoded version of the word 'Dulaca'.",
            "Your password must contain a valid color hex code.",
            "Your password must have the year that Filipino tennis player Alex Eala debuted in professional tennis. The year must be written in base 2 format.",
            "The length of your password must be a prime number.",
            "Your password must contain the answer to this question 'Complete the line from one of Sabrina Carpenter's songs: 'You fit every stereotype, \"___\"'.",
            "Your password must contain the answer to this question 'Are nondeterministic finite automata more powerful than their equivalent deterministic finite automata?'",
            "The sum of the numbers of your password must be a multiple of 14.",
            "The sum of the roman numerals of your password must be a multiple of 21 (only uppercase letters count for roman numerals)."
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
        
        # Your password must contain the sum of the numbers of the current hour and day today mod 7
        elif "sum of the numbers of the current hour and day today mod 7" in rule_lower:
            now = datetime.datetime.now()
            sum_value = (now.hour + now.day) % 7
            return str(sum_value) in password
        
        # The digits of your password must sum up to a multiple of 141
        elif "digits of your password must sum up to a multiple of 141" in rule_lower:
            digit_sum = sum(int(char) for char in password if char.isdigit())
            return digit_sum > 0 and digit_sum % 141 == 0
        
        # Your password must contain one Japanese hiragana character
        elif "contain one japanese hiragana character" in rule_lower:
            # Hiragana Unicode range: U+3040 to U+309F
            return any('\u3040' <= char <= '\u309F' for char in password)
        
        # Your password must contain the 46th-50th decimal digits of pi
        elif "46th-50th decimal digits of pi" in rule_lower:
            pi_digits = "37510"  # 46th-50th decimal digits of pi
            return pi_digits in password
        
        # Your password must contain the first two words of Franz Kafka's "The Metamorphosis"
        elif "first two words of franz kafka" in rule_lower and "metamorphosis" in rule_lower:
            return "One morning" in password or "one morning" in password.lower()
        
        # Your password must contain an anagram of the word "secure"
        elif "anagram of the word 'secure'" in rule_lower:
            secure_letters = sorted("secure")
            # Check all 6-letter substrings for anagrams
            for i in range(len(password) - 5):
                substring = password[i:i+6].lower()
                if sorted(substring) == secure_letters:
                    return True
            return False
        
        # Add the reversed name of the inventor of the world's first computer program
        elif "reversed name of the inventor of the world's first computer program" in rule_lower:
            # Ada Lovelace -> "adA" (first name reversed) or "ecalevoL" (last name reversed)
            password_lower = password.lower()
            return "ada" in password_lower or "eclaya" in password_lower or "ecalvol" in password_lower
        
        # From a finite alphabet Σ, how many strings can be made?
        elif "from a finite alphabet" in rule_lower and "how many strings can be made" in rule_lower:
            return "countably infinite" in password.lower() or "countably_infinite" in password.lower()
        
        # Your password must include a prime number sandwiched between two hash signs
        elif "prime number sandwiched between two hash signs" in rule_lower:
            # Common primes to check for
            primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113]
            for prime in primes:
                if f"#{prime}#" in password:
                    return True
            return False
        
        # From the grammar: S → aSb | ab. What are the only valid strings of length 4?
        elif "grammar" in rule_lower and "asb" in rule_lower and "valid strings of length 4" in rule_lower:
            return "aabb" in password
        
        # Your password must contain a string in the language defined by (a*(ab | bb)*)
        elif "regular expression" in rule_lower and "a*(ab | bb)*" in rule_lower:
            # Check for patterns like: a, aa, ab, bb, aab, abb, abab, abbb, etc.
            regex_pattern = r'a*(ab|bb)*'
            return bool(re.search(regex_pattern, password))
        
        # Include a base64-encoded version of the word "Dulaca"
        elif "base64-encoded version of the word 'dulaca'" in rule_lower:
            return "RHVsYWNh" in password  # base64.b64encode("Dulaca".encode()).decode()
        
        # Your password must contain a valid color hex code
        elif "valid color hex code" in rule_lower:
            # Match hex color codes like #FF0000, #123456, etc.
            hex_pattern = r'#[0-9A-Fa-f]{6}'
            return bool(re.search(hex_pattern, password))
        
        # Alex Eala debut year in base 2 format
        elif "alex eala debuted" in rule_lower and "base 2 format" in rule_lower:
            return "11111100100" in password  # 2020 in binary
        
        # The length of your password must be a prime number
        elif "length of your password must be a prime number" in rule_lower:
            length = len(password)
            if length < 2:
                return False
            for i in range(2, int(length ** 0.5) + 1):
                if length % i == 0:
                    return False
            return True
        
        # Sabrina Carpenter song lyric completion
        elif "sabrina carpenter" in rule_lower and "you fit every stereotype" in rule_lower:
            return "Send a pic" in password or "send a pic" in password.lower()
        
        # Are nondeterministic finite automata more powerful?
        elif "nondeterministic finite automata more powerful" in rule_lower:
            return "no" in password.lower()
        
        # The sum of the numbers of your password must be a multiple of 14
        elif "sum of the numbers of your password must be a multiple of 14" in rule_lower:
            numbers = re.findall(r'\d+', password)
            if not numbers:
                return False
            number_sum = sum(int(num) for num in numbers)
            return number_sum % 14 == 0
        
        # The sum of the roman numerals must be a multiple of 21
        elif "sum of the roman numerals" in rule_lower and "multiple of 21" in rule_lower:
            roman_values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
            total = sum(roman_values.get(char, 0) for char in password if char in roman_values)
            return total > 0 and total % 21 == 0
        
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
import re
from typing import List, Dict, Set, Tuple, Optional
import random
import datetime
import base64
import logging

# Set up logging for rule validation debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            "The sum of the roman numerals of your password must be a multiple of 21 (only uppercase letters count for roman numerals).",
            "Your password must include an answer to a riddle. The riddle is: What has keys but can't open locks?",
            "Your password must mention a fruit, but only one that contains potassium and is featured in Mario Kart.",
            "Your password must include the phrase 'ilovecmsc141'",
            "Your password must contain a decimal number and its equivalent octal number. There should be one of the digits of its equivalent hexadecimal numbers in between the decimal and its equivalent octal number.",
            "Your password must contain what is being asked from this: 'Caesar shifted his message to you: WXMXKFBGBLMBVYBGBMXTNMHFTMHG. He told you to go to the 45th street and deliver this message to Mr. Decriptor. Mr. Decriptor said something to you. What did he say to you?'",
            "Your password must contain one of the names of the people who made this game.",
            "Your password must contain the title of this game in reverse order. (answer: 'gnirtS laniF ehT')",
            "Your password must contain the answer to this question: 'What Hollywood star joined the list of 19 EGOT winners with their delayed win in the Grammys in 1994?'"
            "Your password must include a legal move in standard chess notation.",
            "Your password must contain its own length as a number.",
            "Your password must include the current time.",
            "Your password must contain the currency symbol used in Japan.",
            "Your password must include today's day of the week.",
            "Your password must include the number of the current month.",
            "Your password must include the name of a planet."
        ]
        
        # Cache for performance optimization
        self._validation_cache: Dict[Tuple[str, str], bool] = {}
        self._cache_hits = 0
        self._cache_misses = 0
    
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
            logger.warning(f"Requested {count} rules but only {len(available_rules)} available after exclusions")
            return available_rules.copy()
    
    def _is_prime(self, n: int) -> bool:
        """Helper method to check if a number is prime"""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(n ** 0.5) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    def _validate_decimal_octal_hex_pattern(self, password: str) -> bool:
        """
        Enhanced validation for decimal/octal/hex pattern.
        Looks for pattern: [decimal][hex_digit][octal] where all represent the same number.
        """
        try:
            # Look for patterns like: 15F17 (15 decimal, F from hex, 17 octal)
            # Pattern: decimal number + hex digit + octal number
            pattern = r'(\d+)([0-9A-Fa-f])(\d+)'
            matches = re.findall(pattern, password)
            
            for decimal_str, hex_digit, octal_str in matches:
                try:
                    decimal_num = int(decimal_str)
                    octal_num = int(octal_str, 8)  # Parse as octal
                    
                    # Check if decimal and octal represent the same number
                    if decimal_num == octal_num:
                        # Get the hex representation and check if hex_digit is in it
                        hex_repr = hex(decimal_num)[2:].upper()  # Remove '0x' prefix
                        if hex_digit.upper() in hex_repr:
                            logger.info(f"Valid decimal/octal/hex pattern found: {decimal_str}{hex_digit}{octal_str}")
                            return True
                except ValueError:
                    # Invalid octal number, continue checking
                    continue
            
            # Also check some common valid examples as fallback
            valid_examples = [
                "15F17",   # 15 decimal = 17 octal, hex F is in F
                "8190",    # 8 decimal = 10 octal, hex digit 1 is in 8's hex
                "10B12",   # 10 decimal = 12 octal, hex digit B is valid
                "7B7",     # 7 decimal = 7 octal, hex digit B is valid
                "9A11",    # 9 decimal = 11 octal, hex digit A is valid
                "12C14",   # 12 decimal = 14 octal, hex digit C is valid
                "16D20"    # 16 decimal = 20 octal, hex digit D is valid
            ]
            return any(example in password for example in valid_examples)
            
        except Exception as e:
            logger.error(f"Error in decimal/octal/hex validation: {e}")
            return False
    
    def _parse_roman_numerals(self, text: str) -> int:
        """
        Parse Roman numerals from text and return their total value.
        Handles subtractive notation correctly (IV=4, IX=9, XL=40, XC=90, CD=400, CM=900).
        """
        roman_values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        
        # Find all Roman numeral sequences in the text
        roman_pattern = r'[IVXLCDM]+'
        roman_sequences = re.findall(roman_pattern, text)
        
        total = 0
        for sequence in roman_sequences:
            sequence_value = 0
            i = 0
            while i < len(sequence):
                current_char = sequence[i]
                current_value = roman_values.get(current_char, 0)
                
                # Check if this is a subtractive case
                if i + 1 < len(sequence):
                    next_char = sequence[i + 1]
                    next_value = roman_values.get(next_char, 0)
                    
                    # Subtractive notation rules
                    if (current_char == 'I' and next_char in 'VX') or \
                       (current_char == 'X' and next_char in 'LC') or \
                       (current_char == 'C' and next_char in 'DM'):
                        sequence_value += (next_value - current_value)
                        i += 2  # Skip both characters
                        continue
                
                sequence_value += current_value
                i += 1
            
            total += sequence_value
            logger.info(f"Found Roman numeral sequence: '{sequence}' = {sequence_value}")
        
        return total
    
    def _validate_palindrome(self, password: str, length: int) -> bool:
        """Check for palindromes of specific length in the password"""
        for i in range(len(password) - length + 1):
            substring = password[i:i+length]
            if substring.lower() == substring.lower()[::-1]:
                logger.info(f"Found {length}-character palindrome: {substring}")
                return True
        return False
    
    def validate_rule(self, password: str, rule: str) -> bool:
        """Validate password against a single rule with enhanced logic and caching"""
        
        # Check cache first for performance
        cache_key = (password, rule)
        if cache_key in self._validation_cache:
            self._cache_hits += 1
            return self._validation_cache[cache_key]
        
        self._cache_misses += 1
        rule_lower = rule.lower()
        
        try:
            result = self._validate_rule_internal(password, rule, rule_lower)
            
            # Cache the result
            self._validation_cache[cache_key] = result
            
            # Log validation result for debugging
            logger.debug(f"Rule validation - Password: {password[:20]}{'...' if len(password) > 20 else ''} | Rule: {rule[:50]}{'...' if len(rule) > 50 else ''} | Result: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating rule '{rule[:50]}...': {e}")
            return False
    
    def _validate_rule_internal(self, password: str, rule: str, rule_lower: str) -> bool:
        """Internal method containing all rule validation logic"""
        
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
        # EXTENDED RULE VALIDATION (Enhanced)
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
            return self._validate_palindrome(password, 7)
        
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
            # Use regex to find all numbers between hash signs
            hash_pattern = r'#(\d+)#'
            matches = re.findall(hash_pattern, password)
            
            for match in matches:
                try:
                    number = int(match)
                    if self._is_prime(number):
                        logger.info(f"Found valid prime number between hash signs: #{number}#")
                        return True
                except ValueError:
                    continue
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
            return self._is_prime(len(password))
        
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
            return self._parse_roman_numerals(password) % 21 == 0
        
        # Your password must include an answer to a riddle: What has keys but can't open locks?
        elif "riddle" in rule_lower and "what has keys but can't open locks" in rule_lower:
            password_lower = password.lower()
            return "piano" in password_lower or "keyboard" in password_lower
        
        # Your password must mention a fruit that contains potassium and is featured in Mario Kart
        elif "fruit" in rule_lower and "potassium" in rule_lower and "mario kart" in rule_lower:
            password_lower = password.lower()
            return "banana" in password_lower
        
        # Your password must include the phrase "ilovecmsc141"
        elif "include the phrase" in rule_lower and "ilovecmsc141" in rule_lower:
            return "ilovecmsc141" in password
        
        # Enhanced decimal, octal, hexadecimal number relationship validation
        elif "decimal number and its equivalent octal number" in rule_lower and "hexadecimal" in rule_lower:
            return self._validate_decimal_octal_hex_pattern(password)
        
        # Caesar cipher solution: DETERMINISTICFINITEAUTOMATON
        elif "caesar shifted" in rule_lower and "wxmxkfbgblmbvybgbmxtnmhftmhg" in rule_lower:
            return "DETERMINISTICFINITEAUTOMATON" in password
        
        # Names of the game makers
        elif "names of the people who made this game" in rule_lower:
            names = ["Jason", "John", "Bisuela", "Christian", "Brillos", "Joanalyn", "Cadampog", "Berk", "Stephen", "Cutamora"]
            password_lower = password.lower()
            return any(name.lower() in password_lower for name in names)
        
        # Title of the game in reverse order
        elif "title of this game in reverse order" in rule_lower:
            return "gnirtS laniF ehT" in password
        
        # EGOT winner with delayed Grammy win in 1994
        elif "hollywood star" in rule_lower and "egot winners" in rule_lower and "grammys in 1994" in rule_lower:
            password_lower = password.lower()
            return "audrey hepburn" in password_lower or "audrey" in password_lower or "hepburn" in password_lower

        # Legal move in standard chess notation
        elif "legal move in standard chess notation" in rule_lower:
            # Check for common chess moves in algebraic notation
            chess_patterns = [
                r'[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8][+#]?',  # Standard moves (e.g., Nf3, Bxe5, Qd8+)
                r'O-O(-O)?[+#]?',  # Castling (O-O or O-O-O)
                r'[a-h]x[a-h][1-8][+#]?',  # Pawn captures (e.g., exd5)
                r'[a-h][1-8]=[QRBN][+#]?',  # Pawn promotion (e.g., a8=Q)
                r'[a-h][1-8]',  # Simple pawn moves (e.g., e4, d5)
            ]
            
            for pattern in chess_patterns:
                if re.search(pattern, password):
                    return True
            
            # Also check for some common specific moves
            common_moves = [
                "e4", "d4", "Nf3", "Nc3", "Bb5", "Be2", "Qd1", "Kg1", "Rf1",
                "a4", "b4", "c4", "f4", "g4", "h4", "a5", "b5", "c5", "d5", 
                "e5", "f5", "g5", "h5", "Nbd2", "Nge2", "O-O", "O-O-O"
            ]
            return any(move in password for move in common_moves)
        
        # Length as a number
        elif "contain its own length as a number" in rule_lower:
            return len(password) > 0 and str(len(password)) in password
        
        # Current time
        elif "current time" in rule_lower:
            now = datetime.datetime.now()
            # Accept various time formats
            time_formats = [
                f"{now.hour}:{now.minute:02d}",  # HH:MM (e.g., "14:30")
                f"{now.hour}:{now.minute}",      # H:M (e.g., "14:3")
                f"{now.strftime('%I:%M %p')}",   # 12-hour format (e.g., "2:30 PM")
                f"{now.strftime('%I:%M%p')}",    # 12-hour no space (e.g., "2:30PM")
                f"{now.hour}{now.minute:02d}",   # HHMM (e.g., "1430")
                str(now.hour),                   # Just hour (e.g., "14")
                str(now.minute)                  # Just minute (e.g., "30")
            ]
            return any(time_format in password for time_format in time_formats)
        
        # Currency symbol used in Japan
        elif "currency symbol used in japan" in rule_lower:
            return any(symbol in password for symbol in ["¥", "￥"])
        
        # Today's day of the week
        elif "today's day of the week" in rule_lower:
            now = datetime.datetime.now()
            password_lower = password.lower()
            day_formats = [
                now.strftime("%A").lower(),      # Full name (e.g., "monday")
                now.strftime("%a").lower(),      # Abbreviated (e.g., "mon")
                now.strftime("%A"),              # Full name proper case
                now.strftime("%a")               # Abbreviated proper case
            ]
            return any(day_format in password_lower for day_format in day_formats)
        
        # Current month
        elif "current month" in rule_lower:
            now = datetime.datetime.now()
            return str(now.month) in password
        
        # Name of a planet
        elif "name of a planet" in rule_lower:
            planets = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
            password_lower = password.lower()
            return any(planet.lower() in password_lower for planet in planets)
        
        # Default case - unknown rule
        return True
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache performance statistics"""
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2),
            "cache_size": len(self._validation_cache)
        }
    
    def clear_cache(self):
        """Clear the validation cache"""
        self._validation_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        logger.info("Validation cache cleared")

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
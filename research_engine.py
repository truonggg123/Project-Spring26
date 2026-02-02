"""
Search Engine Module - Trie Implementation for Autocomplete
Author: Dang Khoa
Purpose: Provide fast word suggestions using Prefix Tree (Trie) data structure
"""
"""
FFmpeg Installation As noted in your previous status, Whisper requires FFmpeg to process audio files.
Windows: Download from gyan.dev, extract it, and add the bin folder to your System PATH variables.
"""
class TrieNode:
    """Node in the Trie tree"""
    def __init__(self):
        self.children = {}  # Dictionary to store child nodes (key: character, value: TrieNode)
        self.is_end_of_word = False  # Flag to mark end of a valid word
        self.word = None  # Store the complete word at the end node for easy retrieval


class Trie:
    """Trie (Prefix Tree) implementation for efficient word searching"""
    
    def __init__(self):
        self.root = TrieNode()
        self.word_count = 0
    
    def insert_word(self, word):
        """
        Insert a word into the Trie
        
        Args:
            word (str): Word to insert (will be converted to lowercase)
        
        Time Complexity: O(m) where m is the length of the word
        """
        if not word:
            return
        
        word = word.lower().strip()
        if not word:
            return
        
        current_node = self.root
        
        # Traverse through each character in the word
        for char in word:
            # If character doesn't exist, create a new node
            if char not in current_node.children:
                current_node.children[char] = TrieNode()
            
            # Move to the next node
            current_node = current_node.children[char]
        
        # Mark the end of word and store the complete word
        if not current_node.is_end_of_word:
            current_node.is_end_of_word = True
            current_node.word = word
            self.word_count += 1
    
    def search_word(self, word):
        """
        Check if a word exists in the Trie
        
        Args:
            word (str): Word to search for
        
        Returns:
            bool: True if word exists, False otherwise
        
        Time Complexity: O(m) where m is the length of the word
        """
        word = word.lower().strip()
        current_node = self.root
        
        for char in word:
            if char not in current_node.children:
                return False
            current_node = current_node.children[char]
        
        return current_node.is_end_of_word
    
    def get_suggestions(self, prefix, max_suggestions=10):
        """
        Get word suggestions based on a prefix
        
        Args:
            prefix (str): The prefix to search for
            max_suggestions (int): Maximum number of suggestions to return
        
        Returns:
            list: List of suggested words starting with the prefix
        
        Time Complexity: O(p + n) where p is prefix length, n is number of nodes explored
        """
        if not prefix:
            return []
        
        prefix = prefix.lower().strip()
        current_node = self.root
        
        # Navigate to the prefix node
        for char in prefix:
            if char not in current_node.children:
                return []  # Prefix not found
            current_node = current_node.children[char]
        
        # Collect all words with this prefix using DFS
        suggestions = []
        self._collect_words(current_node, suggestions, max_suggestions)
        
        return suggestions[:max_suggestions]
    
    def _collect_words(self, node, suggestions, max_suggestions):
        """
        Helper method to collect words using Depth-First Search (DFS)
        
        Args:
            node (TrieNode): Current node
            suggestions (list): List to store found words
            max_suggestions (int): Maximum number of suggestions
        """
        if len(suggestions) >= max_suggestions:
            return
        
        # If current node marks end of word, add it to suggestions
        if node.is_end_of_word and node.word:
            suggestions.append(node.word)
        
        # Recursively explore all children (alphabetically sorted for consistent results)
        for char in sorted(node.children.keys()):
            if len(suggestions) >= max_suggestions:
                break
            self._collect_words(node.children[char], suggestions, max_suggestions)
    
    def get_word_count(self):
        """Return the total number of words in the Trie"""
        return self.word_count


class SearchEngine:
    """Main search engine class using Trie for autocomplete"""
    
    def __init__(self):
        self.trie = Trie()
        self._load_common_words()
    
    def _load_common_words(self):
        """
        Load common English words into the Trie
        This includes ~1000 most common English words for practice
        """
        # Common English words for pronunciation practice
        # Organized by category for better educational value
        
        common_words = [
            # Basic pronouns and articles (10)
            "i", "you", "he", "she", "it", "we", "they", "the", "a", "an",
            
            # Common verbs (50)
            "be", "have", "do", "say", "go", "get", "make", "know", "think", "take",
            "see", "come", "want", "use", "find", "give", "tell", "work", "call", "try",
            "ask", "need", "feel", "become", "leave", "put", "mean", "keep", "let", "begin",
            "seem", "help", "show", "hear", "play", "run", "move", "like", "live", "believe",
            "bring", "happen", "write", "sit", "stand", "lose", "pay", "meet", "include", "continue",
            
            # Common nouns (100)
            "time", "year", "people", "way", "day", "man", "thing", "woman", "life", "child",
            "world", "school", "state", "family", "student", "group", "country", "problem", "hand", "part",
            "place", "case", "week", "company", "system", "program", "question", "work", "government", "number",
            "night", "point", "home", "water", "room", "mother", "area", "money", "story", "fact",
            "month", "lot", "right", "study", "book", "eye", "job", "word", "business", "issue",
            "side", "kind", "head", "house", "service", "friend", "father", "power", "hour", "game",
            "line", "end", "member", "law", "car", "city", "community", "name", "president", "team",
            "minute", "idea", "kid", "body", "information", "back", "parent", "face", "others", "level",
            "office", "door", "health", "person", "art", "war", "history", "party", "result", "change",
            "morning", "reason", "research", "girl", "guy", "moment", "air", "teacher", "force", "education",
            
            # Common adjectives (80)
            "good", "new", "first", "last", "long", "great", "little", "own", "other", "old",
            "right", "big", "high", "different", "small", "large", "next", "early", "young", "important",
            "few", "public", "bad", "same", "able", "late", "hard", "left", "best", "better",
            "true", "full", "special", "easy", "clear", "recent", "certain", "personal", "open", "red",
            "difficult", "available", "likely", "short", "single", "medical", "current", "happy", "free", "low",
            "sure", "common", "poor", "natural", "significant", "similar", "hot", "dead", "central", "successful",
            "dark", "various", "entire", "close", "legal", "religious", "cold", "final", "main", "green",
            "nice", "huge", "popular", "traditional", "cultural", "strong", "particular", "beautiful", "economic", "cold",
            
            # Common adverbs (40)
            "not", "also", "very", "just", "well", "so", "only", "then", "now", "how",
            "even", "back", "there", "still", "too", "really", "never", "here", "much", "always",
            "perhaps", "quite", "almost", "often", "probably", "already", "especially", "either", "ever", "sometimes",
            "together", "away", "however", "later", "today", "usually", "far", "again", "yesterday", "forward",
            
            # Common prepositions (30)
            "in", "on", "at", "by", "for", "with", "about", "as", "into", "from",
            "to", "of", "through", "over", "after", "between", "out", "against", "during", "without",
            "before", "under", "around", "among", "across", "above", "off", "behind", "below", "near",
            
            # Common conjunctions (15)
            "and", "but", "or", "because", "if", "when", "while", "although", "since", "unless",
            "until", "whether", "than", "though", "whereas",
            
            # Technology and modern terms (50)
            "computer", "internet", "phone", "website", "email", "software", "technology", "digital", "online", "app",
            "data", "network", "social", "media", "video", "mobile", "screen", "device", "user", "system",
            "password", "file", "download", "upload", "search", "click", "message", "post", "share", "connect",
            "wireless", "laptop", "keyboard", "mouse", "monitor", "printer", "camera", "battery", "signal", "update",
            "install", "delete", "save", "open", "close", "copy", "paste", "cut", "select", "enter",
            
            # Food and cooking (50)
            "food", "eat", "drink", "cook", "meal", "breakfast", "lunch", "dinner", "restaurant", "kitchen",
            "recipe", "ingredient", "taste", "delicious", "healthy", "fresh", "sweet", "sour", "spicy", "bitter",
            "vegetable", "fruit", "meat", "fish", "chicken", "beef", "pork", "rice", "bread", "cheese",
            "milk", "egg", "butter", "sugar", "salt", "pepper", "oil", "water", "tea", "coffee",
            "juice", "sandwich", "pizza", "pasta", "salad", "soup", "cake", "cookie", "dessert", "snack",
            
            # Travel and places (50)
            "travel", "trip", "journey", "vacation", "holiday", "tourist", "visit", "destination", "airport", "flight",
            "hotel", "restaurant", "museum", "park", "beach", "mountain", "river", "lake", "ocean", "forest",
            "city", "town", "village", "country", "nation", "continent", "island", "bridge", "building", "street",
            "road", "highway", "train", "bus", "car", "taxi", "subway", "station", "ticket", "passport",
            "luggage", "suitcase", "map", "direction", "north", "south", "east", "west", "guide", "tour",
            
            # Weather and nature (50)
            "weather", "sunny", "cloudy", "rainy", "windy", "stormy", "foggy", "snowy", "temperature", "hot",
            "warm", "cool", "cold", "freezing", "humid", "dry", "climate", "season", "spring", "summer",
            "autumn", "fall", "winter", "rain", "snow", "wind", "storm", "thunder", "lightning", "cloud",
            "sun", "moon", "star", "sky", "nature", "tree", "flower", "plant", "grass", "leaf",
            "animal", "bird", "fish", "insect", "dog", "cat", "horse", "cow", "wild", "environment",
            
            # Health and body (50)
            "health", "healthy", "sick", "ill", "disease", "medicine", "doctor", "hospital", "patient", "nurse",
            "pain", "hurt", "injury", "treatment", "therapy", "exercise", "fitness", "diet", "nutrition", "vitamin",
            "body", "head", "face", "eye", "ear", "nose", "mouth", "tooth", "neck", "shoulder",
            "arm", "hand", "finger", "chest", "stomach", "back", "leg", "foot", "toe", "skin",
            "blood", "heart", "brain", "bone", "muscle", "breath", "sleep", "rest", "tired", "energy",
            
            # Education (50)
            "education", "school", "university", "college", "student", "teacher", "professor", "class", "course", "lesson",
            "subject", "study", "learn", "teach", "exam", "test", "grade", "score", "homework", "assignment",
            "book", "textbook", "notebook", "pen", "pencil", "paper", "desk", "classroom", "library", "laboratory",
            "science", "math", "history", "geography", "language", "literature", "art", "music", "physics", "chemistry",
            "biology", "english", "reading", "writing", "speaking", "listening", "knowledge", "skill", "degree", "diploma",
            
            # Work and business (50)
            "work", "job", "career", "profession", "occupation", "business", "company", "office", "employee", "employer",
            "boss", "manager", "director", "executive", "worker", "staff", "team", "colleague", "client", "customer",
            "meeting", "project", "task", "deadline", "schedule", "appointment", "interview", "resume", "salary", "wage",
            "income", "profit", "loss", "budget", "cost", "price", "sale", "marketing", "product", "service",
            "quality", "quantity", "efficiency", "productivity", "performance", "success", "failure", "achievement", "goal", "target",
            
            # Emotions and feelings (50)
            "happy", "sad", "angry", "excited", "nervous", "worried", "afraid", "scared", "surprised", "shocked",
            "confused", "tired", "bored", "interested", "curious", "satisfied", "disappointed", "frustrated", "embarrassed", "ashamed",
            "proud", "grateful", "thankful", "sorry", "guilty", "jealous", "envious", "lonely", "homesick", "nostalgic",
            "calm", "peaceful", "relaxed", "stressed", "anxious", "depressed", "hopeful", "optimistic", "pessimistic", "confident",
            "shy", "brave", "courageous", "kind", "friendly", "generous", "selfish", "mean", "rude", "polite",
            
            # Time expressions (40)
            "today", "tomorrow", "yesterday", "now", "then", "soon", "later", "early", "late", "before",
            "after", "during", "while", "meanwhile", "recently", "lately", "currently", "presently", "forever", "never",
            "always", "usually", "often", "sometimes", "rarely", "seldom", "once", "twice", "again", "still",
            "yet", "already", "just", "moment", "instant", "second", "minute", "hour", "daily", "weekly",
            
            # Common phrases components (50)
            "please", "thank", "thanks", "welcome", "sorry", "excuse", "pardon", "hello", "goodbye", "bye",
            "yes", "no", "okay", "sure", "maybe", "perhaps", "certainly", "absolutely", "definitely", "probably",
            "understand", "mean", "matter", "care", "mind", "remember", "forget", "realize", "recognize", "imagine",
            "suppose", "guess", "assume", "expect", "hope", "wish", "want", "need", "like", "love",
            "hate", "prefer", "enjoy", "appreciate", "admire", "respect", "trust", "believe", "doubt", "wonder",
            
            # Difficult pronunciation words (30)
            "through", "tough", "enough", "cough", "thought", "bought", "taught", "caught", "daughter", "aughter",
            "knight", "knife", "know", "knot", "psychology", "psychiatrist", "receipt", "scissors", "island", "debris",
            "colonel", "salmon", "mortgage", "wednesday", "february", "schedule", "chaos", "choir", "pneumonia", "mischievous",
        ]
        
        print(f"Loading {len(common_words)} words into Trie...")
        
        for word in common_words:
            self.insert_word(word)
        
        print(f"✓ Successfully loaded {self.trie.get_word_count()} unique words into search engine")
    
    def insert_word(self, word):
        """
        Insert a word into the search engine
        
        Args:
            word (str): Word to insert
        """
        self.trie.insert_word(word)
    
    def search_word(self, word):
        """
        Check if a word exists in the search engine
        
        Args:
            word (str): Word to search for
        
        Returns:
            bool: True if word exists, False otherwise
        """
        return self.trie.search_word(word)
    
    def get_suggestions(self, prefix, max_suggestions=10):
        """
        Get word suggestions for a given prefix
        
        Args:
            prefix (str): The prefix to search for
            max_suggestions (int): Maximum number of suggestions (default: 10)
        
        Returns:
            list: List of suggested words
        """
        return self.trie.get_suggestions(prefix, max_suggestions)
    
    def get_statistics(self):
        """
        Get statistics about the search engine
        
        Returns:
            dict: Dictionary containing statistics
        """
        return {
            "total_words": self.trie.get_word_count(),
            "data_structure": "Trie (Prefix Tree)",
            "time_complexity_insert": "O(m)",
            "time_complexity_search": "O(m)",
            "time_complexity_suggestions": "O(p + n)",
            "space_complexity": "O(ALPHABET_SIZE * N * M)"
        }


# Global instance for easy import
_search_engine_instance = None

def get_search_engine():
    """
    Get or create the global SearchEngine instance (Singleton pattern)
    
    Returns:
        SearchEngine: The global search engine instance
    """
    global _search_engine_instance
    if _search_engine_instance is None:
        _search_engine_instance = SearchEngine()
    return _search_engine_instance


# Testing and demonstration
if __name__ == "__main__":
    print("=" * 60)
    print("SEARCH ENGINE TESTING - TRIE DATA STRUCTURE")
    print("=" * 60)
    
    # Create search engine
    engine = get_search_engine()
    
    # Display statistics
    print("\n📊 Search Engine Statistics:")
    stats = engine.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test cases
    print("\n" + "=" * 60)
    print("TEST CASES")
    print("=" * 60)
    
    test_prefixes = ["th", "pro", "hap", "comp", "bea", "str", "edu"]
    
    for prefix in test_prefixes:
        suggestions = engine.get_suggestions(prefix, max_suggestions=8)
        print(f"\n🔍 Prefix: '{prefix}'")
        print(f"   Suggestions: {', '.join(suggestions)}")
    
    # Test word search
    print("\n" + "=" * 60)
    print("WORD SEARCH TEST")
    print("=" * 60)
    
    test_words = ["hello", "computer", "xyz123", "beautiful", "notaword"]
    for word in test_words:
        exists = engine.search_word(word)
        status = "✓ Found" if exists else "✗ Not found"
        print(f"   {status}: '{word}'")
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)
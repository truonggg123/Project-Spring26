class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False


class Trie:

    def __init__(self):
        self.root = TrieNode()

    # chèn từ
    def insert_word(self, word):

        node = self.root

        for char in word:

            if char not in node.children:
                node.children[char] = TrieNode()

            node = node.children[char]

        node.is_end = True


    # tìm node theo prefix
    def _find_node(self, prefix):

        node = self.root

        for char in prefix:

            if char not in node.children:
                return None

            node = node.children[char]

        return node


    # DFS lấy tất cả từ
    def _dfs(self, node, prefix, results):

        if node.is_end:
            results.append(prefix)

        for char in node.children:
            self._dfs(node.children[char], prefix + char, results)


    # lấy gợi ý
    def get_suggestions(self, prefix):

        node = self._find_node(prefix)

        if not node:
            return []

        results = []

        self._dfs(node, prefix, results)

        return results


# khởi tạo trie
trie = Trie()

# danh sách từ
word_list = [
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


# nạp từ vào Trie
for word in word_list:
    trie.insert_word(word)


if __name__ == "__main__":
    while True:

        prefix = input("Nhập prefix: ")

        suggestions = trie.get_suggestions(prefix)

        if suggestions:
            print("Gợi ý:", suggestions[:10])
        else:
            print("Không có từ phù hợp")
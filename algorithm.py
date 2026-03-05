import math

def levenshtein_matrix(seq1, seq2):
    """
    Generates the Levenshtein distance matrix using 2D array (Dynamic Programming).
    Works for both strings (character-level) and lists of words (token-level).
    
    Args:
        seq1: Source sequence (Target)
        seq2: Destination sequence (User Input)
        
    Returns:
        2D list representing the DP matrix.
    """
    rows = len(seq1) + 1
    cols = len(seq2) + 1
    
    # Initialize 2D array
    matrix = [[0 for _ in range(cols)] for _ in range(rows)]

    # Base cases
    for i in range(rows):
        matrix[i][0] = i
    for j in range(cols):
        matrix[0][j] = j

    # Fill matrix
    for i in range(1, rows):
        for j in range(1, cols):
            # Cost is 0 if items match, else 1
            cost = 0 if seq1[i-1] == seq2[j-1] else 1
            
            matrix[i][j] = min(
                matrix[i-1][j] + 1,      # Deletion
                matrix[i][j-1] + 1,      # Insertion
                matrix[i-1][j-1] + cost  # Substitution / Match
            )
            
    return matrix

def get_pronunciation_score(s1, s2):
    """
    Calculates a score (0-100) based on character-level Levenshtein distance.
    
    Args:
        s1: Target string (Sample sentence)
        s2: User input string
        
    Returns:
        float: Score between 0 and 100
    """
    if s1 is None: s1 = ""
    if s2 is None: s2 = ""
    
    # Normalize strings
    s1 = s1.lower().strip()
    s2 = s2.lower().strip()
    
    if not s1 and not s2:
        return 100.0
    if not s1 or not s2:
        return 0.0

    # Get matrix
    matrix = levenshtein_matrix(s1, s2)
    
    # The Levenshtein distance is the value in the bottom-right cell
    distance = matrix[-1][-1]
    
    # Calculate score based on the length of the longer string
    max_len = max(len(s1), len(s2))
    
    if max_len == 0:
        return 100.0
        
    score = (1 - distance / max_len) * 100
    return max(0.0, round(score, 2))

def compare_words(s1, s2):
    """
    Performs word-by-word comparison to generate colored feedback.
    
    Args:
        s1: Target string (Sample)
        s2: User input string (Spoken)
        
    Returns:
        List of dictionaries containining 'word' and 'color' (green/red).
        Example: [{'word': 'hello', 'color': 'green'}, {'word': 'word', 'color': 'red'}]
    """
    if s1 is None: s1 = ""
    if s2 is None: s2 = ""
    
    # Tokenize into words
    words1 = s1.lower().strip().split()
    words2 = s2.strip().split() # Keep case for display if needed, but compare lower
    
    # Create comparison version for logic
    words2_lower = [w.lower() for w in words2]
    
    matrix = levenshtein_matrix(words1, words2_lower)
    
    # Backtrack to find alignment
    i, j = len(words1), len(words2)
    alignment = []
    
    while i > 0 or j > 0:
        # Prio 1: Match (Diagonal with no cost)
        # Note: We check words2_lower for comparison
        if i > 0 and j > 0 and words1[i-1] == words2_lower[j-1]:
            alignment.append({"word": words2[j-1], "color": "green", "status": "correct"})
            i -= 1
            j -= 1
            
        # Prio 2: Substitution (Diagonal with cost)
        # We classify substitution as 'red' (incorrect)
        elif i > 0 and j > 0 and matrix[i][j] == matrix[i-1][j-1] + 1:
            alignment.append({"word": words2[j-1], "color": "red", "status": "substitution"})
            i -= 1
            j -= 1
            
        # Prio 3: Insertion (Left) - User said an extra word
        # We mark extra words as red (or maybe grey/yellow if spec allowed, but "red for incorrect" covers this)
        elif j > 0 and matrix[i][j] == matrix[i][j-1] + 1:
            alignment.append({"word": words2[j-1], "color": "red", "status": "insertion"})
            j -= 1
            
        # Prio 4: Deletion (Up) - User missed a word
        # Since we only return User's words colored, we don't return the deleted word in the list of "user words".
        # However, to keep the flow correct, we just decrement i.
        # If we wanted to show missing words, we could add them with a special color.
        elif i > 0 and matrix[i][j] == matrix[i-1][j] + 1:
            # alignment.append({"word": f"[{words1[i-1]}]", "color": "gray"}) # Optional: Show missing
            i -= 1
            
        else:
            # Fallback for complex overlapping cases, usually shouldn't happen with standard logical priority
            # If we are here, we prioritize moving towards smaller indices
            if j > 0:
                alignment.append({"word": words2[j-1], "color": "red", "status": "unknown"})
                j -= 1
            elif i > 0:
                i -= 1

    # Reverse because we backtracked
    return alignment[::-1]

if __name__ == "__main__":
    # Test Cases
    print("=== Testing Levenshtein Algorithm ===")
    
    # 1. Exact Match
    t1 = "Hello world"
    u1 = "Hello world"
    print(f"\nTarget: '{t1}'\nUser:   '{u1}'")
    print(f"Score: {get_pronunciation_score(t1, u1)}")
    print(f"Highlight: {compare_words(t1, u1)}")
    
    # 2. Minor differences
    t2 = "The quick brown fox"
    u2 = "The quick brwn fox" # Typo
    print(f"\nTarget: '{t2}'\nUser:   '{u2}'")
    print(f"Score: {get_pronunciation_score(t2, u2)}")
    print(f"Highlight: {compare_words(t2, u2)}")
    
    # 3. Major differences
    t3 = "I like to code"
    u3 = "I love coding" 
    print(f"\nTarget: '{t3}'\nUser:   '{u3}'")
    print(f"Score: {get_pronunciation_score(t3, u3)}")
    print(f"Highlight: {compare_words(t3, u3)}")
    
    # 4. Extra/Missing words
    t4 = "This is a test"
    u4 = "This is test" # 'a' missing
    print(f"\nTarget: '{t4}'\nUser:   '{u4}'")
    print(f"Score: {get_pronunciation_score(t4, u4)}")
    print(f"Highlight: {compare_words(t4, u4)}")

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

import os

# nạp từ vào Trie
import os
txt_path = os.path.join(os.path.dirname(__file__), "google-10000-english-usa.txt")
try:
    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            word = line.strip().lower()
            if word:
                trie.insert_word(word)
except Exception as e:
    print("Cannot load google-10000-english-usa.txt:", e)


if __name__ == "__main__":
    while True:

        prefix = input("Nhập prefix: ")

        suggestions = trie.get_suggestions(prefix)

        if suggestions:
            print("Gợi ý:", suggestions[:10])
        else:
            print("Không có từ phù hợp")
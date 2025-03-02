from random import choice
import random
import yaml
from rich.console import Console
import collections
import numpy as np
import heapq


class Guesser:
    """
    A class to handle guessing logic for a Wordle-like game.
    """

    def __init__(self, manual):
        """
        Initialize the Guesser.

        Args:
            manual (str): If 'manual', the user will input guesses manually.
        """
        self.word_list = yaml.load(open('wordlist.yaml'), Loader=yaml.FullLoader)
        self.base_wordlist = self.word_list.copy()  # Store full word list
        self._manual = manual
        self.console = Console()
        self._tried = []
        self._excluded_letters = set()

    def restart_game(self):
        """Reset the game state."""
        self._tried = []
        self._excluded_letters = set()
        self.word_list = self.base_wordlist.copy()

    def get_letter_frequencies(self, words):
        """Calculate letter frequency across a list of words."""
        letter_counts = collections.Counter("".join(words))
        total_letters = sum(letter_counts.values())

        return {char: count / total_letters for char, count in letter_counts.items()}

    def get_letter_position_frequencies(self, words):
        """Calculate frequency of each letter in each position."""
        position_counts = [collections.defaultdict(float) for _ in range(5)]
        for word in words:
            for i, char in enumerate(word):
                c=[]
                c.append(char)
                if char not in c:
                    position_counts[i][char] += 1
                else:
                    position_counts[i][char] += (1/2)

        total_words = len(words)
        return [{char: count / total_words for char, count in counter.items()} for counter in position_counts]

    def entropy(self, word, words):
        """Calculate entropy of a word based on possible outcomes."""
        pattern_dict = collections.defaultdict(list)

        for possible_word in words:
            pattern = self.get_pattern(word, possible_word)
            pattern_dict[pattern].append(possible_word)

        entropy_value = 0
        total_words = len(words)

        for pattern, words in pattern_dict.items():
            p = len(words) / total_words
            entropy_value -= p * np.log2(p)

        return entropy_value

    def get_pattern(self, guess, target):
        """Generate Wordle feedback pattern for a guess against a target word."""
        result = ["+"] * 5
        target_chars = list(target)

        for i in range(5):
            if guess[i] == target[i]:
                result[i] = guess[i]
                target_chars[i] = None

        for i in range(5):
            if result[i] == "+" and guess[i] in target_chars:
                result[i] = "-"
                target_chars[target_chars.index(guess[i])] = None

        return "".join(result)

    def filter_words(self, last_guess, feedback):
        """Filter words based on feedback from the previous guess."""
        self.word_list = [word for word in self.word_list if self.get_pattern(last_guess, word) == feedback]

    def get_guess(self, result):
        """
        Determine the next guess based on feedback.

        Args:
            result (str): Feedback pattern from the previous guess.

        Returns:
            str: The next guessed word.
        """
        if self._manual == 'manual':
            return self.console.input('Your guess:\n')

        if result and self._tried:
            self.filter_words(self._tried[-1], result)

        if not self.word_list:
            self.word_list = self.base_wordlist.copy()
            self.console.print("Warning: No possible words left. Resetting word list.")

        self.console.print(f"Remaining words: {len(self.word_list)}")
        base_word_list = self.base_wordlist

        if len(self._tried) < 1:
            """First guess based on full word list letter & position frequencies."""
            letter_freq = self.get_letter_frequencies(self.word_list)  
            position_freq = self.get_letter_position_frequencies(self.word_list)  

            word_scores = {
                word: sum(letter_freq.get(c, 0) for c in set(word)) +
                      sum(position_freq[i].get(word[i], 0) for i in range(5))
                for word in base_word_list
            }

            # **Use `heapq.nlargest()` to get top-ranked word efficiently**
            guess = heapq.nlargest(1, base_word_list, key=lambda w: word_scores[w])[0]

        elif len(self.word_list) > 100:
            """Second guess based on letter frequencies from remaining words, ranked by full list."""
            letter_freq_remaining = self.get_letter_frequencies(self.word_list)  
            position_freq_remaining = self.get_letter_position_frequencies(self.word_list)  

            word_scores = {
                word: sum(letter_freq_remaining.get(c, 0) for c in set(word)) +
                      sum(position_freq_remaining[i].get(word[i], 0) for i in range(5))
                for word in base_word_list
            }

            ranked_words = heapq.nlargest(len(base_word_list), base_word_list, key=lambda w: word_scores[w])

            first_guess_letters = set(self._tried[0])

            # **Use `set.intersection()` for faster filtering**
            for word in ranked_words:
                if not set(word).intersection(first_guess_letters):  
                    guess = word
                    break
            else:
                guess = ranked_words[0]

 

        else:
            """Handle one missing letter scenario efficiently."""
            known_positions = [i for i, c in enumerate(result) if c.isalpha()]
            unknown_positions = [i for i, c in enumerate(result) if c == "+"]

            if len(unknown_positions) == 1 and len(known_positions) == 4 and len(self.word_list) > 2 and len(self._tried) < 5:
                missing_index = unknown_positions[0]
                possible_letters = {word[missing_index] for word in self.word_list}
                confirmed_letters = {c for i, c in enumerate(result) if c.isalpha()}

                possible_letters -= confirmed_letters
                
                possible_letters=list(possible_letters)
                result=[]
                if len(possible_letters)>=5:
                    for _ in range(5):
                        result.append(possible_letters[_])
                
                else:
                    for i in possible_letters:
                        result.append(i)
                    for i in range(5-len(result)):
                        result.append('x')
                if result.count('x')>=4:
                    guess = max(self.word_list, key=lambda w: self.entropy(w, self.word_list))
                else:
                    guess="".join(result)
#belki her tryda ayni degeri seciyordur o yuzden yanlis cikiyor olabilir. etropy degil de randomly secsek?                    
          
            else:
                """Use entropy-based selection if multiple unknowns exist."""
                guess = max(self.word_list, key=lambda w: self.entropy(w, self.word_list))

        self._tried.append(guess)
        self.console.print(f"Next guess: {guess}")
        return guess
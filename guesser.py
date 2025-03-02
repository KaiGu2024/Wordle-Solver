import yaml
import numpy as np
from rich.console import Console
import collections
import math
from collections import Counter
from functools import lru_cache

class Guesser:
    def __init__(self, manual):
        self.word_list = yaml.load(open('wordlist.yaml'), Loader=yaml.FullLoader)
        # self.word_freq = self._load_word_freq("wordlist.tsv")  
        self.base_wordlist = self.word_list.copy()
        self._manual = manual
        self.console = Console()
        self._tried = []
     #   self._precompute_pattern_cache()

        # frequency for performance optimization
        # self.letter_freq = self.get_letter_frequencies(self.base_wordlist)
        # self.position_freq = self.get_letter_position_frequencies(self.base_wordlist)

        # precompute scores for performance optimization
        self._precomputed_scores = self._precompute_entropy_scores()
        # self._precomputed_distinguish = self._precompute_distinguish_scores()

        # precompute optimal first guess
        # if "aires" in self.base_wordlist:
        #   self.optimal_first_guess = "aires"
        # else:
        self._precomputed_scores = self._precompute_entropy_scores()
        self.optimal_first_guess = max(self._precomputed_scores, key=self._precomputed_scores.get)
    
    """
    def _load_word_freq(self, filename):
        raw_freq = {}
        with open(filename, "r") as file:
            next(file)  # first line is header
            for line in file:
                parts = line.strip().split("\t")
                if len(parts) == 3:
                    index, word, freq = parts
                    raw_freq[word] = int(freq)
        
        sorted_words = sorted(raw_freq.items(), key=lambda x: -x[1])
        return {word: (i / len(sorted_words)) for i, (word, _) in enumerate(sorted_words)}
    """
    
    """
    def get_letter_frequencies(self, words):
        letter_counts = collections.Counter("".join(words))
        total_letters = sum(letter_counts.values())
        return {char: count / total_letters for char, count in letter_counts.items()}

    def get_letter_position_frequencies(self, words):
        position_counts = [collections.defaultdict(float) for _ in range(5)]
        for word in words:
            for i, char in enumerate(word):
                position_counts[i][char] += 1
        total_words = len(words)
        return [{char: count / total_words for char, count in counter.items()} for counter in position_counts]
    """
    
    def restart_game(self):
        self._tried = []
        self.word_list = self.base_wordlist.copy()

    #def _precompute_pattern_cache(self):
    #    self.pattern_cache = {guess: {target: self.get_pattern(guess, target) for target in self.base_wordlist}for guess in self.base_wordlist}

    def _precompute_entropy_scores(self):
        """first guess"""
        return {
            word: self.entropy(word, self.base_wordlist) * 0.9 # + self.word_freq.get(word, 0) * 0.1
            for word in self.base_wordlist
        }

    '''
    def _precompute_distinguish_scores(self):
        """precompute distinguish scores"""
        return {
            word: self.distinguish_score(word, self.base_wordlist)
            for word in self.base_wordlist
        }
    '''

    def entropy(self, word, words):
        """entropy"""
        pattern_counts = Counter(self.get_pattern(word, pw) for pw in words)
        total = len(words)
        return -sum((count/total) * math.log2(count/total) for count in pattern_counts.values())

    @lru_cache(maxsize=None)
    def get_pattern(self, guess, target):
        """get pattern using cache"""
        counts = Counter(target)
        results = []
        for i, letter in enumerate(guess):
            if letter == target[i]:
                results.append(letter)
                counts[guess[i]] -= 1
            else:
                results.append('+')
        for i, letter in enumerate(guess):
            if guess[i] != target[i] and guess[i] in target:
                if counts[guess[i]] > 0:
                    results[i] = '-'
                    counts[guess[i]] -= 1
        return "".join(results)

    def distinguish_score(self, word, candidates):
        """score"""
        return len({self.get_pattern(word, target) for target in candidates})

    def filter_words(self, last_guess, feedback):
        """filter words"""
        target_char_counts = Counter(last_guess[i] for i, c in enumerate(feedback) if c != '+')
        self.word_list = [
            word for word in self.word_list
            if self.get_pattern(last_guess, word) == feedback
            and all(word.count(c) >= req for c, req in target_char_counts.items())
        ]

    def get_guess(self, feedback):
        """get guess"""
        if self._manual == 'manual':
            return self.console.input('Your guess:\n')

        if feedback and self._tried:
            self.filter_words(self._tried[-1], feedback)

        possible_words = [w for w in self.word_list if w not in self._tried]

        # guess in different circumstances
        if len(self._tried) == 0:
            guess = self.optimal_first_guess
        #elif len(possible_words) <= 3:
        #    """choose the most frequent word"""
        #    guess = max(possible_words, key=lambda w: self.word_freq[w])
        elif len(self._tried) == 1 and len(possible_words) > 3:
            external_candidates = [w for w in self.base_wordlist if w not in self._tried]
            size_factor = len(possible_words) / len(self.base_wordlist)
            
            # weight adjustment
            entropy_weight = 0.7 + 0.2 * (1 - size_factor)
            distinguish_weight = 0.3 - 0.1 * size_factor

            # distinguish scores
            distinguish_scores = {
                w: self.distinguish_score(w, possible_words) 
                for w in possible_words[:500]  # in case of performance issue
            }

            guess = max(
                external_candidates,
                key=lambda w: (
                    self.entropy(w, possible_words)  * entropy_weight +
                    distinguish_scores.get(w, 1) * distinguish_weight
                )
            )
        else:
            guess = max(possible_words, key=lambda w: self.entropy(w, possible_words))

        """
        else:
            # possible_words 内的 letter 频率
            possible_letter_counts = collections.Counter("".join(possible_words))
            total_possible_letters = sum(possible_letter_counts.values())
            possible_letter_freq = {char: count / total_possible_letters for char, count in possible_letter_counts.items()}

            # possible_words 内的 position 频率
            possible_position_counts = [collections.defaultdict(float) for _ in range(5)]
            for word in possible_words:
                for i, char in enumerate(word):
                    possible_position_counts[i][char] += 1
            total_possible_words = len(possible_words)
            possible_position_freq = [{char: count / total_possible_words for char, count in counter.items()} for counter in possible_position_counts]

           # 选择具有最高字母和位置频率的单词
            guess = max(
                possible_words,
                key=lambda w: possible_letter_freq.get(w, 0) + sum(possible_position_freq[i].get(w[i], 0) for i in range(5))
            )
        """
        self._tried.append(guess)
        self.console.print(f"Next guess: [bold green]{guess}[/bold green]")
        return guess
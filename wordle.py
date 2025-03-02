from random import choice, seed
import yaml
from collections import Counter

class Wordle():
    
    global ALLOWED_GUESSES, word_list
    ALLOWED_GUESSES = 6
    word_list = yaml.load(open('wordlist.yaml'), Loader=yaml.FullLoader)
    
    # comment this out for development, use for testing / marking
    seed(42)

    def __init__(self, random_state=None):
        self._word = choice(word_list)
        self._tried = []

    def restart_game(self, random_state=None):
        self._word = choice(word_list)
        self._tried = []
        self._endgame = False

    def get_matches(self, guess):
        # Produces the feedback string
        counts = Counter(self._word)
        results = []
        for i, letter in enumerate(guess):
            if guess[i] == self._word[i]:
                results+=guess[i]
                counts[guess[i]]-=1
            else:
                results+='+'
        for i, letter in enumerate(guess):
            if guess[i] != self._word[i] and guess[i] in self._word:
                if counts[guess[i]]>0:
                    counts[guess[i]]-=1
                    results[i]='-'

        return ''.join(results)

    def check_guess(self, guess):

        result = False
        end_game = False
        guess = guess.lower().strip()

        if not guess.isalpha():
            return "Please enter only letters", False
        if len(guess) != 5:
            return "Please enter a five-letter word", False
        elif guess in self._tried:
            return "You have already tried that word", False
        else:
            self._tried.append(guess)
            if guess == self._word:
                end_game = True
                result = self._word
                print('Congratulations, you guessed the word!')
            else:
                result = self.get_matches(guess)
                if len(self._tried) == ALLOWED_GUESSES:
                    print(f'Sorry, you did not guess the word. The word was {self._word}', )
                    end_game = True
        return result, end_game
    

    

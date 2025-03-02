# Wordle-Solver
Assignment 1: Write a Wordle solver



Your task is to write a guesser for the game Wordle (or a close cousin). Wordle is a word-guessing game - you have 6 attempts to guess a 5-letter word. You can play it here https://www.nytimes.com/games/wordle/index.html.

With each guess, you learn whether you correctly guessed a character (and its position), whether a character appears in the word but in a different position, or does not appear in the word at all. 



The Assignment:



The program contains three classes (with pretty self-explanatory names):

- game.py: runs n games of Wordle coordinating the other two classes and keeps track of the scores.

- wordle.py: implements the game of Wordle, from choosing the word to guess to checking the correctness of a guess.

- guesser.py: produces a guess word. This is where you will be doing all your work. (At the moment it just returns a random word from the list.)

You also have a list of ~4K words along with their frequency in a corpus in a tab-separated file (and in yaml format).

Game creates a new guesser object for every run. 

You can run 10 games of Wordle with the following command:

   python game.py --r 10

When you run it, program will output some stats about your success rate. 



You need to modify guesser.py to produce a best-guess. Your submission has to be in the form of a .py Python file, which we can import for scoring. We provide you with a template for that file. 



Your guess.py must include a get_guess() method that: 

- takes feedback from a previous guess ('+', '-', or a letter)

- returns a single string (your best guess)

IMPORTANT: Do NOT modify wordle.py or game.py, or your submission might crash. Using any variable or function of the World object that gives you a clue is cheating and will be graded 0!



The assignment is graded on the train and secret test set in terms of:

- How often your guesser correctly guesses the word

- The average number of tries it takes

This will be compared to a simple heuristic-based approach.

Bonus points will be given to the best-scoring solutions. 

Note that some of the words we test on will not be in your list (different from the original game, where all words are known), so your guesser has to handle unseen words.

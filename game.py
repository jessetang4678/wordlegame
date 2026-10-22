"""Game logic for Wordle Race. No Flask in this file: it only knows about games."""

import random
import secrets
import string

WORD_LENGTH = 5
MAX_GUESSES = 6

# Temporary word list. In a later commit we'll fetch a real list from the web.
WORDS = [
    "CRANE", "SLATE", "PLANT", "GHOST", "BRICK", "FLAME", "SHARK", "TOAST",
    "MONEY", "PIANO", "LEMON", "CHAIR", "RIVER", "STORM", "QUEEN", "WORLD",
]

# Every game lives here, keyed by its 4-letter code.
# It's just a Python dictionary in memory, so games disappear when the server restarts.
games = {}


def score_guess(guess, answer):
    """Return a list of 5 colors ("green", "yellow" or "gray") for a guess.

    Done in two passes so repeated letters are handled like real Wordle:
    guessing SPEED against ABIDE marks only ONE E yellow, because ABIDE has one E.
    """
    colors = ["gray"] * WORD_LENGTH
    leftover = []  # letters of the answer that weren't matched exactly

    # Pass 1: exact matches are green.
    for i in range(WORD_LENGTH):
        if guess[i] == answer[i]:
            colors[i] = "green"
        else:
            leftover.append(answer[i])

    # Pass 2: right letter, wrong spot is yellow, but only as many times
    # as that letter is still left over in the answer.
    for i in range(WORD_LENGTH):
        if colors[i] != "green" and guess[i] in leftover:
            colors[i] = "yellow"
            leftover.remove(guess[i])

    return colors


class Game:
    def __init__(self, code, word):
        self.code = code
        self.word = word        # the secret word: never sent to the browser
        self.players = []       # secret player IDs; index 0 is Player 1, index 1 is Player 2
        self.guesses = {}       # player ID -> list of (guess, colors) pairs
        self.winner = None      # player ID of whoever solved it first
        self.rematch_code = None  # code of the follow-up game, once someone asks for a rematch

    def add_player(self):
        """Add a player and return their secret ID, or None if the game is full."""
        if self.is_full():
            return None
        player_id = secrets.token_urlsafe(6)
        self.players.append(player_id)
        self.guesses[player_id] = []
        return player_id

    def is_full(self):
        return len(self.players) >= 2

    def player_number(self, player_id):
        """Return 1 or 2 for a valid player ID, or None if it isn't in this game."""
        if player_id in self.players:
            return self.players.index(player_id) + 1
        return None

    def opponent_of(self, player_id):
        """Return the other player's ID, or None if nobody has joined yet."""
        for other in self.players:
            if other != player_id:
                return other
        return None

    def out_of_guesses(self, player_id):
        return len(self.guesses[player_id]) >= MAX_GUESSES

    def is_over(self):
        """The game ends when someone wins, or when both players run out of guesses."""
        if self.winner is not None:
            return True
        return self.is_full() and all(self.out_of_guesses(p) for p in self.players)

    def can_guess(self, player_id):
        return self.is_full() and not self.is_over() and not self.out_of_guesses(player_id)

    def outcome_for(self, player_id):
        """Return "won", "lost", "draw", or None if the game is still going."""
        if self.winner == player_id:
            return "won"
        if self.winner is not None:
            return "lost"
        if self.is_over():
            return "draw"
        return None

    def make_guess(self, player_id, guess):
        """Try a guess. Return an error message for the player, or None if it worked."""
        guess = guess.strip().upper()

        if not self.is_full():
            return "Wait for your opponent to join before guessing."
        if self.is_over():
            return "This game is already over."
        if self.out_of_guesses(player_id):
            return "You don't have any guesses left."
        if len(guess) != WORD_LENGTH or not guess.isalpha():
            return f"A guess must be exactly {WORD_LENGTH} letters."

        self.guesses[player_id].append((guess, score_guess(guess, self.word)))
        if guess == self.word:
            self.winner = player_id   # first correct guess wins the race
        return None

    def start_rematch(self):
        """Create a new game with the same two players and a new word.

        If the other player already asked for a rematch, reuse that game.
        Returns the new game.
        """
        if self.rematch_code is None:
            new_game = start_new_game()
            for player_id in self.players:   # same IDs, so both players' links keep working
                new_game.players.append(player_id)
                new_game.guesses[player_id] = []
            self.rematch_code = new_game.code
        return games[self.rematch_code]


def new_code():
    """Make a random 4-letter code that no other game is using."""
    while True:
        code = "".join(random.choices(string.ascii_uppercase, k=4))
        if code not in games:
            return code


def start_new_game():
    code = new_code()
    game = Game(code, random.choice(WORDS))
    games[code] = game
    return game
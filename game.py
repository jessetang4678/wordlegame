"""Game logic for Wordle Race. No Flask in this file: it only knows about games."""

import random
import secrets
import string

# Temporary word list. In a later commit we'll fetch a real list from the web.
WORDS = [
    "CRANE", "SLATE", "PLANT", "GHOST", "BRICK", "FLAME", "SHARK", "TOAST",
    "MONEY", "PIANO", "LEMON", "CHAIR", "RIVER", "STORM", "QUEEN", "WORLD",
]

# Every game lives here, keyed by its 4-letter code.
# It's just a Python dictionary in memory, so games disappear when the server restarts.
games = {}


class Game:
    def __init__(self, code, word):
        self.code = code
        self.word = word        # the secret word: never sent to the browser
        self.players = []       # secret player IDs; index 0 is Player 1, index 1 is Player 2

    def add_player(self):
        """Add a player and return their secret ID, or None if the game is full."""
        if self.is_full():
            return None
        player_id = secrets.token_urlsafe(6)
        self.players.append(player_id)
        return player_id

    def is_full(self):
        return len(self.players) >= 2

    def player_number(self, player_id):
        """Return 1 or 2 for a valid player ID, or None if it isn't in this game."""
        if player_id in self.players:
            return self.players.index(player_id) + 1
        return None


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

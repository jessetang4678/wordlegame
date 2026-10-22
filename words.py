"""Word lists for Wordle Race.

- SECRET_WORDS: common words the server picks the answer from (kept here, so they're never obscure).
- Allowed guesses: about 14,800 five-letter words downloaded from GitHub with `requests`
  when the server starts. If that website doesn't answer, we fall back to accepting
  any 5 letters, so the game still works offline.
"""

import requests

WORD_LIST_URL = "https://raw.githubusercontent.com/tabatkins/wordle-list/main/words"

SECRET_WORDS = [
    "ABOUT", "ALERT", "APPLE", "BEACH", "BLAME", "BRAIN", "BREAD", "BRICK", "BRUSH", "CANDY",
    "CHAIR", "CHALK", "CHARM", "CHEST", "CLOUD", "COAST", "CRANE", "CROWN", "DANCE", "DREAM",
    "DRINK", "EAGLE", "EARTH", "FAITH", "FEAST", "FIELD", "FLAME", "FLOOR", "FRESH", "FRUIT",
    "GHOST", "GIANT", "GLASS", "GRAPE", "GRASS", "HEART", "HONEY", "HOUSE", "JUICE", "KNIFE",
    "LAUGH", "LEMON", "LIGHT", "MAGIC", "MONEY", "MOUSE", "MUSIC", "NIGHT", "NURSE", "OCEAN",
    "PAINT", "PARTY", "PEACH", "PIANO", "PILOT", "PLANE", "PLANT", "PLATE", "PRIZE", "QUEEN",
    "QUIET", "RADIO", "RIVER", "ROBOT", "ROUND", "SHARK", "SHEEP", "SHIRT", "SKATE", "SLATE",
    "SLEEP", "SMILE", "SNAKE", "SPACE", "SPOON", "STONE", "STORM", "SUGAR", "SWEET", "TABLE",
    "TIGER", "TOAST", "TOWER", "TRAIN", "TRUCK", "VOICE", "WATER", "WHALE", "WORLD", "YOUTH",
]


def load_allowed_guesses():
    """Download the list of allowed guesses.

    Returns (set_of_words, None) on success, or (None, message) if the website
    didn't answer, so the app can tell the players instead of crashing.
    """
    try:
        response = requests.get(WORD_LIST_URL, timeout=5)
        response.raise_for_status()   # treat 404, 500, etc. as failures too
    except requests.RequestException:
        return None, "Couldn't download the dictionary, so any 5 letters count as a guess."

    words = {line.strip().upper() for line in response.text.splitlines()}
    words = {w for w in words if len(w) == 5 and w.isalpha()}
    if not words:
        return None, "The dictionary download was empty, so any 5 letters count as a guess."

    words.update(SECRET_WORDS)   # make sure every possible answer is also an allowed guess
    return words, None


# Runs once, when the server starts.
ALLOWED_GUESSES, WORD_LIST_WARNING = load_allowed_guesses()


def is_allowed(guess):
    """True if the guess is in the dictionary (or if we have no dictionary)."""
    return ALLOWED_GUESSES is None or guess in ALLOWED_GUESSES

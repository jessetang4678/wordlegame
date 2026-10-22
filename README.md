# Wordle Game

A two-player Wordle race built with Flask. Both players get the same secret word, and the first one to guess it wins. You see your own letters and colors, and your opponent's board updates live, showing their colors but never their letters.

## Features

- Create a game and share a 4-letter code; the second player joins with the code
- Standard Wordle scoring (green, yellow, gray), including repeated letters
- Live opponent progress without refreshing the page
- Win, lose or draw, with the word revealed at the end, plus a one-click rematch
- Guesses are checked against a dictionary of about 14,800 words, downloaded at startup
- Friendly error pages: bad codes, full games, invalid guesses, broken links, and a fallback if the dictionary website doesn't answer

## Setup

Requires Python 3.

```bash
git clone <this repository's URL>
cd wordlegame
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run it

```bash
flask --app app run --port 5001
```

Then open http://localhost:5001.

**Mac note:** port 5000 is often taken by macOS's AirPlay Receiver, which is why these instructions use port 5001.

## How to play

1. In a normal browser window, open http://localhost:5001 and click **Create game**.
2. Open a second window in incognito/private mode (it acts as a second player), go to the same address, and enter the game code.
3. Both players type 5-letter guesses. The first to find the word wins.

Games are kept in memory, so restarting the server clears them.

## How it works

**The server (Flask)** stores every game in a Python dictionary. It picks the secret word, scores each guess, and decides who wins. The secret word never leaves the server until the game is over. Each player is identified by a private link (`/game/<code>/p/<player-id>`), so no logins or cookies are needed.

**The browser** shows the board and sends guesses through a form. A small script (`static/game.js`) asks the server every second for the game's state as JSON (a technique called polling) and redraws the opponent's tiles, or reloads the page when the game changes (opponent joined, game over, rematch).

## Project structure

```
app.py              Flask routes and error pages
game.py             Game rules: scoring, turns, winning, rematches
words.py            Secret words and the downloaded dictionary (uses requests)
templates/          HTML pages (Jinja templates)
static/style.css    Styling
static/game.js      Live updates in the browser
```

## Built with

Flask, requests, and an AI assistant (Claude), which I used to plan the features, write the code one feature at a time, and explain how each part works.
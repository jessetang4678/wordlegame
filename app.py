from flask import Flask, jsonify, redirect, render_template, request, url_for

from game import MAX_GUESSES, WORD_LENGTH, games, start_new_game

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/create", methods=["POST"])
def create_game():
    game = start_new_game()
    player_id = game.add_player()
    return redirect(url_for("play", code=game.code, player_id=player_id))


@app.route("/join", methods=["POST"])
def join_game():
    code = request.form.get("code", "").strip().upper()

    if len(code) != 4 or not code.isalpha():
        return render_template("home.html", error="A game code is exactly 4 letters."), 400

    game = games.get(code)
    if game is None:
        return render_template("home.html", error=f"There's no game with code {code}."), 404

    if game.is_full():
        return render_template("home.html", error=f"Game {code} already has two players."), 409

    player_id = game.add_player()
    return redirect(url_for("play", code=game.code, player_id=player_id))


def find_player(code, player_id):
    """Look up a game and player. Return (game, None) if valid, or (None, error page) if not."""
    game = games.get(code.upper())
    if game is None:
        return None, (render_template(
            "error.html",
            message="That game doesn't exist. Games are lost when the server restarts, so try creating a new one.",
        ), 404)

    if game.player_number(player_id) is None:
        return None, (render_template("error.html", message="That player link isn't valid for this game."), 404)

    return game, None


def show_board(game, player_id, error=None):
    """Render the game page for one player."""
    return render_template(
        "game.html",
        game=game,
        player_id=player_id,
        number=game.player_number(player_id),
        my_guesses=game.guesses[player_id],
        opponent_guesses=game.guesses.get(game.opponent_of(player_id), []),
        can_guess=game.can_guess(player_id),
        outcome=game.outcome_for(player_id),
        out_of_guesses=game.out_of_guesses(player_id),
        max_guesses=MAX_GUESSES,
        word_length=WORD_LENGTH,
        error=error,
    )


@app.route("/game/<code>/p/<player_id>")
def play(code, player_id):
    game, error_page = find_player(code, player_id)
    if error_page:
        return error_page
    return show_board(game, player_id)


@app.route("/game/<code>/p/<player_id>/guess", methods=["POST"])
def guess(code, player_id):
    game, error_page = find_player(code, player_id)
    if error_page:
        return error_page

    error = game.make_guess(player_id, request.form.get("guess", ""))
    if error:
        return show_board(game, player_id, error=error), 400

    # Redirect after a successful guess so refreshing the page doesn't resubmit it.
    return redirect(url_for("play", code=game.code, player_id=player_id))


@app.route("/game/<code>/p/<player_id>/rematch", methods=["POST"])
def rematch(code, player_id):
    game, error_page = find_player(code, player_id)
    if error_page:
        return error_page

    if not game.is_over():
        return show_board(game, player_id, error="You can only start a rematch once the game is over."), 400

    new_game = game.start_rematch()
    return redirect(url_for("play", code=new_game.code, player_id=player_id))


@app.route("/game/<code>/p/<player_id>/state")
def state(code, player_id):
    """JSON that the browser asks for every second (see static/game.js).

    It only includes what this player is allowed to see: never the secret word,
    and only the colors of the opponent's guesses, not their letters.
    """
    game = games.get(code.upper())
    if game is None or game.player_number(player_id) is None:
        return jsonify(error="This game no longer exists."), 404

    opponent = game.opponent_of(player_id)
    return jsonify(
        full=game.is_full(),
        over=game.is_over(),
        rematch_code=game.rematch_code,
        opponent_colors=[colors for _, colors in game.guesses.get(opponent, [])],
    )
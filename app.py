from flask import Flask, redirect, render_template, request, url_for

from game import games, start_new_game

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


@app.route("/game/<code>/p/<player_id>")
def play(code, player_id):
    game = games.get(code.upper())
    if game is None:
        return render_template(
            "error.html",
            message="That game doesn't exist. Games are lost when the server restarts, so try creating a new one.",
        ), 404

    number = game.player_number(player_id)
    if number is None:
        return render_template("error.html", message="That player link isn't valid for this game."), 404

    return render_template("game.html", game=game, number=number)
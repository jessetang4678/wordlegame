from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/create", methods=["POST"])
def create_game():
    # Placeholder: real game creation comes in commit 3
    return "Creating games is coming in the next step."


@app.route("/join", methods=["POST"])
def join_game():
    code = request.form.get("code", "").strip().upper()
    if len(code) != 4 or not code.isalpha():
        return render_template("home.html", error="A game code is exactly 4 letters."), 400
    # Placeholder: real joining comes in commit 3
    return f"Joining game {code} is coming in the next step."
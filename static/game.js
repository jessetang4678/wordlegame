// Live updates for the game page.
//
// Every second, ask the server for this game's state (as JSON) and update the page:
// - the opponent's colors are filled in without reloading, so your typing isn't lost
// - for bigger changes (opponent joined, game over, rematch ready) the page reloads,
//   because the server then needs to draw a different page

const page = document.getElementById("game");
const stateUrl = page.dataset.stateUrl;

// What the page looked like when the server drew it.
const shown = {
  full: page.dataset.full === "true",
  over: page.dataset.over === "true",
  rematchCode: page.dataset.rematch || null,
};

const connection = document.getElementById("connection");

function drawOpponent(allColors) {
  const rows = document.querySelectorAll("#opponent-board .row");
  rows.forEach((row, i) => {
    const colors = allColors[i];  // undefined if they haven't made this guess yet
    row.querySelectorAll(".tile").forEach((tile, j) => {
      tile.className = "tile " + (colors ? colors[j] : "empty");
    });
  });
}

async function checkForUpdates() {
  try {
    const response = await fetch(stateUrl);
    const state = await response.json();

    if (!response.ok) {
      // The server answered, but the game is gone (for example, it was restarted).
      connection.textContent = state.error;
      connection.hidden = false;
      return;  // stop polling
    }

    connection.hidden = true;

    if (state.full !== shown.full || state.over !== shown.over ||
        state.rematch_code !== shown.rematchCode) {
      location.reload();
      return;
    }

    drawOpponent(state.opponent_colors);
  } catch (err) {
    // The server didn't answer at all (stopped, or the network dropped). Keep trying.
    connection.textContent = "Can't reach the server. Trying again…";
    connection.hidden = false;
  }

  setTimeout(checkForUpdates, 1000);
}

checkForUpdates();

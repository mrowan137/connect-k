"""Connect-k game.

Flask-based Python web-game game called `Connect-k`, a 2-player game where
players take turns placing pieces onto the bottom row of an infinite grid. The
game ends if a player's pieces form a contiguous line (horizontal or vertical)
of length `k`. The supported gameplay
options are:
  - Value of `k`: length of the line required to win
  - Player color: red or blue
  - Player to go first: red or blue
  - Opponent: computer (easy), computer (hard), human

"""

from collections import defaultdict
from uuid import uuid4

from wtforms import Form, IntegerField, SelectField, validators
from flask import (
  Flask, session, request, make_response, render_template,
  render_template_string, redirect, url_for, escape
)


class Input(Form):
  """Connect-k player can select game options."""
  k = IntegerField(
    label="Select a value for k: ",
    default=3,
    render_kw={"style": "width: 100%"},
    validators=[
      validators.InputRequired(), validators.NumberRange(
        min=1,
        max=2147483647,
        message=("Input a number in the range [0, 2147483647]!")
      )
    ]
  )

  player_color = SelectField(
    label="Choose your color: ",
    default="Red",
    choices=["Red", "Blue"],
    render_kw={"style": "width: 100%"},
    validators=[
      validators.InputRequired(),
      validators.AnyOf(
        ["Red", "Blue"],
        message=("Select Red or Blue."),
        values_formatter=None
      )
    ]
  )

  first_player = SelectField(
    label="Who goes first?",
    default="Red",
    choices=["Red", "Blue"],
    render_kw={"style": "width: 100%"},
    validators=[validators.InputRequired(),
      validators.AnyOf(["Red", "Blue"],
        message=("Select Red or Blue."),
        values_formatter=None
      )
    ]
  )

  opponent = SelectField(
    label="Choose opponent: ",
    default="Computer (easy)",
    choices=["Computer (easy)", "Computer (hard)", "Human"],
    render_kw={"style": "width: 100%"},
    validators=[validators.InputRequired(),
      validators.AnyOf(["Computer (easy)", "Computer (hard)", "Human"],
        message=("Select a Computer or Human."),
        values_formatter=None
      )
    ]
  )


class ConnectK(object):
  """Implementation of Connect-k game."""
  def __init__(
    self, k=None, player_color=None, current_player=None,
    opponent=None, M=10, N=17, game_session=None
  ):
    """Connect-k ctr, either from existing Flask `session` or new game."""
    # Flask session constructor: load the game in progress
    if game_session is not None:
      # `k` in Connect-k
      self.k_ = session["k"]

      # players input and state
      self.player_color_ = session["player_color"]
      self.current_player_ = session["current_player"]
      self.first_player_ = session["first_player"]
      self.opponent_ = session["opponent"]
      self.opponent_color_ = session["opponent_color"]

      # computer state, if computer opponent
      self.computer_difficulty_ = session["computer_difficulty"]
      self.computer_is_thinking_ = session["computer_is_thinking"]

      # initial ranges to display the board
      self.m_ = session["M"]
      self.n_ = session["N"]

      # board
      self.board_ = defaultdict(list)
      for board_entry in session["board"]:
        self.board_[int(board_entry)] = session["board"][board_entry]

      self.SetBoardDisplay_(
        self.m_,
        self.n_,
        session["moves_list"][0] if session["moves_list"] else 0
      )

      # game log
      self.moves_list_ = session["moves_list"]
      self.game_over_ = session["game_over"]

      return

    # new game ctr
    self.k_ = k

    self.player_color_ = player_color
    self.current_player_ = current_player
    self.first_player = current_player
    self.opponent_ = opponent
    self.opponent_color_ = None

    self.computer_difficulty_ = None
    self.computer_is_thinking_ = None

    self.m_ = M
    self.n_ = N

    self.board_ = defaultdict(list)
    self.SetBoardDisplay_(self.m_, self.n_, 0)

    self.moves_list_ = list()
    self.game_over_ = False


  def SetBoardDisplay_(self, m, n, center):
    """Update board display over (m x n) grid around a move `center`."""
    # set row and column coordinates
    self.board_display_ = [["" for j in range(n)] for i in range(m)]
    for j in range(1, n):
      self.board_display_[m - 1][j] = center - n//2 + j

    for i in range(m - 2, -1, -1):
      self.board_display_[(m - 2) - i][0] = i

    # fill in the rest of the board
    for j in range(1, n):
      col = center - n//2 + j
      if col in self.board_:
        for i in range(len(self.board_[col])):
          self.board_display_[m - 2 - i][j] = (
            "R" if self.board_[col][i] == 0 else "B"
          )


  def ResetBoard_(self):
    """Clear board, board display, current player, and reset display dims."""
    self.board_.clear()
    self.current_player_ = None
    self.m_, self.n_ = 10, 17
    self.board_display_ = [["" for j in range(self.n_)] for i in range(self.m_)]
    for j in range(1, self.n_):
      self.board_display_[self.m_ - 1][j] = 0 - self.n_//2 + j
    for i in range(self.m_ - 2, -1, -1):
      self.board_display_[(self.m_ - 2) - i][0] = i


  def CheckForGameOver_(self, player, forecast=False):
    """Check if horizontal or vertical line length `k` for some player."""
    winner = None
    winning_move_i = None
    for j in self.board_:
      # vertical check
      i, count = 0, 0
      while ( i < len(self.board_[j])
        and count < self.k_
        and self.board_[j][i] == player
      ):
        i += 1
        count += 1

      if count == self.k_:
        winner = "R" if player == 0 else "B"
        if not forecast:
          self.game_over_ = True
          self.winner_ = winner

        winning_move_i = 0
        return winner, winning_move_i

      # horizontal check
      i = 0
      while i < len(self.board_[j]):
        if self.board_[j][i] != player:
          i += 1
          continue

        count = 1
        l = j - 1
        while (
          l in self.board_
          and i < len(self.board_[l])
          and self.board_[l][i] == player
        ):
          count += 1
          l -= 1

        r = j + 1
        while (
          r in self.board_
          and i < len(self.board_[r])
          and self.board_[r][i] == player
        ):
          count += 1
          r += 1

        if count >= self.k_:
          winner = "R" if player == 0 else "B"
          if not forecast:
            self.game_over_ = True
            self.winner_ = winner

          winning_move_i = i
          return winner, winning_move_i

        i += 1

    return winner, winning_move_i


  def GameOver_(self):
    """Returns `game over` state."""
    return self.game_over_


  def ToggleCurrentPlayer_(self):
    """Toggle curreny player."""
    self.current_player_ = (self.current_player_ + 1)%2


  def PlayMove_(self, move):
    """Log move to history, play move to board, and toggle current player."""
    # play the move
    self.moves_list_.insert(0, move)
    self.board_[move].insert(0, self.current_player_)

    # update whose turn it is
    self.ToggleCurrentPlayer_()


  def UnplayMove_(self):
    """Undo last move (remove from game log, board, and toggle player)."""
    if len(self.moves_list_) == 0:
      return

    # unplay the move
    self.ToggleCurrentPlayer_()
    move = self.moves_list_.pop(0)
    self.board_[move].pop(0)
    if not self.board_[move]:
      del self.board_[move]


  def UpdateDisplay_(self):
    """Sync board display with board, centered around last move."""
    if not self.moves_list_:
      return

    # update the display
    self.m_ = max(max([len(col) + 1 for col in self.board_.values()]), self.m_)
    self.SetBoardDisplay_(self.m_, self.n_, self.moves_list_[0])


  def ComputeMove_(self, mode):
    """Calculate next computer move, for `easy` or `hard` modes."""
    if not self.moves_list_:
      return 0

    if mode == "hard":
      # consider a move within the range of moves so far
      l, r = min(self.board_) - 1, max(self.board_) + 1
      me = self.current_player_
      opponent = not me

      # if it's a winning move for computer, we'll take it; a draw is OK
      for j in range(l, r+1):
        self.PlayMove_(j)
        computer_winner, _ = self.CheckForGameOver_(
          self.opponent_color_,
          forecast=True
        )
        self.UnplayMove_()
        if computer_winner:
          return j

      return self.moves_list_[0]

    elif mode == "easy":
      # like above, check for win or draw
      l, r = min(self.board_) - 1, max(self.board_) + 1
      me = self.current_player_
      opponent = not me

      for j in range(l, r+1):
        self.PlayMove_(j)
        computer_winner, _ = self.CheckForGameOver_(
          self.opponent_color_,
          forecast=True
        )
        self.UnplayMove_()
        if computer_winner:
          return j

      # if it's a winning move for the computer's
      # opponent (the human), we'll block it
      for j in range(l, r+1):
        self.ToggleCurrentPlayer_()
        self.PlayMove_(j)
        player_winner, player_winning_move_i = self.CheckForGameOver_(
          self.player_color_,
          forecast=True
        )
        self.UnplayMove_()
        self.ToggleCurrentPlayer_()
        if player_winner:
          if (
            j in self.board_
            and self.board_[j]
            and self.board_[j][0] == self.player_color_
            and player_winning_move_i == 0
          ):
            # this could be a vertical or horizontal victory,
            # distinguish by the returned i location
            blocking_move = j
          else:
            if (
              j - 1 in self.board_
              and player_winning_move_i < len(self.board_[j - 1])
              and self.board_[j - 1][player_winning_move_i]
              == self.player_color_
            ):
              blocking_move = j - 1
            else:
              blocking_move = j + 1

          return blocking_move

      # otherwise, take a move that positively weights computer's
      # contiguous blocks and negatively weights human's contiguous blocks
      best_move = 0
      score = float("-inf")
      for j in range(l, r+1):
        self.PlayMove_(j)
        my_contiguous_blocks = self.CountAdjacentBlocks_(me)
        opponent_contiguous_blocks = self.CountAdjacentBlocks_(opponent)
        best_score_so_far = score

        # this is just a weighting chosen on intuition, it could be experimented
        # with for computer to have more aggressive or defensive strategy;
        # also add a small bonus for displacing an opponent piece
        score = max(
          0.0*my_contiguous_blocks - 1.0*opponent_contiguous_blocks + 1e-5*(
            len(self.board_[j]) >= 2 and self.board_[j][1] == opponent
          ),
          best_score_so_far
        )

        # make sure we don't take a move that cause the other player to win
        player_winner, _ = self.CheckForGameOver_(
          self.player_color_,
          forecast=True
        )
        best_move = (
          j if score > best_score_so_far and not player_winner else best_move
        )
        self.UnplayMove_()

      return best_move


  def CountAdjacentBlocks_(self, player):
    """Count adjacent blocks resulting from last move for a player."""
    last_move = self.moves_list_[0]

    # vertical count
    i, count = 0, 0
    while (
      self.board_[last_move]
      and i < len(self.board_[last_move]) - 1
      and self.board_[last_move][i] == player
      and self.board_[last_move][i] == self.board_[last_move][i+1]
    ):
      count += 1
      i += 1

    # horizontal check
    i = 0
    while (
      self.board_[last_move] and i < len(self.board_[last_move])
    ):
      if self.board_[last_move][i] != player:
        i += 1
        continue

      l = last_move - 1
      r = last_move + 1

      if (
        r in self.board_
        and i < len(self.board_[r])
        and self.board_[r][i] == player
      ):
        count += 1
      if (
        l in self.board_
        and i < len(self.board_[l])
        and self.board_[l][i] == player
      ):
        count += 1

      i += 1

    return count


BOARD_DISPLAY_TEMPLATE = """
<!doctype html>
<html>
 <head>
  <title>CONNECT-K</title>
  <link href="/static/style.css" rel="stylesheet" type="text/css">
  {{"<!--"|safe if not ck.computer_is_thinking_}} 
  <script>
   setTimeout(
    function(){
     window.location.href = "{{
      url_for(
       "Play", 
       k=ck.k_, 
       player_color=ck.player_color_,
       first_player=ck.first_player_,
       opponent=ck.opponent_
      ) 
     }}";
    },
    800
   );
  </script>
  {{"-->"|safe if not ck.computer_is_thinking_}}
 </head>
 <body style="text-align:center">
  <h1 style="text-align:center; font-family: 'Press Start 2P';">
   CONNECT-K={{ck.k_}}
  </h1>
  <h2 style="font-family: 'Press Start 2P'">{{msg|safe}}</h2>
  <form action="" method="POST">
   <table style="margin-left:auto; margin-right: auto;">
    {% for i in range(ck.m_) %}
     <tr>
      {% for j in range(ck.n_) %}
       <td>
        <button type="submit"
         class="button {{
          (' big_on_hover' if (i == ck.m_ - 2) 
           and (j != 0) 
           and ck.GameOver_() == False 
           and ck.computer_is_thinking_ == False 
           else ""
          )
         }}
         {{
          (' glowing_border' if (j == ck.n_//2)
           and (i == ck.m_ - 2) 
           and ck.moves_list_
          )
         }}"
         name="move" value="{{
          (0 if not ck.moves_list_ else ck.moves_list_[0]) - ck.n_//2 + j
         }}"
         style="height:50px;
          width:50px;
          border-radius: 4px;
          background-color:{{
           ("Crimson" if ck.board_display_[i][j] == "R" 
            else (
             "DarkBlue" if ck.board_display_[i][j] == "B" else "transparent"
            )
           )
          }};
          color:{{
           "white" if ck.board_display_[i][j] in ["R", "B"] else "black"
          }};
         "
         {{
          ("disabled" if (i != ck.m_ - 2) 
           or (j == 0) 
           or ck.GameOver_() == True 
           or ck.computer_is_thinking_ == True
          )
         }}>
         {{ck.board_display_[i][j]}}
        </button>
       </td>
      {% endfor %}
     </tr>
    {% endfor %}
   </table>
   <button type="submit" name="reset">Start a new game</button>
  </form>
 </body>
</html>
"""


app = Flask(__name__)
app.config["SECRET_KEY"] = "9dda556f72ee403bab999bbc5a6e6808"


def GenerateId():
  """Create an ID (to be used as a game identifier)."""
  return uuid4().__str__()


def LoadGame():
  """Load existing Connect-k game if it's there, otherwise start a new one."""
  if "game_id" in session:
    ck = ConnectK(game_session=session)
  else:
    ck = ConnectK()

  return ck


def SaveGame(game):
  """Save the current game in Flask `session`."""
  if "game_id" not in session:
    unique_id = GenerateId()
    session["game_id"] = unique_id

  session["k"] = game.k_
  session["player_color"] = game.player_color_
  session["current_player"] = game.current_player_
  session["first_player"] = game.first_player_
  session["opponent"] = game.opponent_
  session["computer_difficulty"] = game.computer_difficulty_

  session["M"] = game.m_
  session["N"] = game.n_

  session["board"] = game.board_

  session["moves_list"] = game.moves_list_
  session["game_over"] = game.game_over_

  session["computer_is_thinking"] = game.computer_is_thinking_
  session["opponent_color"] = game.opponent_color_


@app.route("/", methods=["GET", "POST"])
def Root():
  """Page for set game input."""
  if "game_id" in session:
    del session["game_id"]

  form = Input(request.form)
  if request.method == "POST" and form.validate():
    response = make_response(
      redirect(
        url_for(
          "Play",
          k=str(escape(form.k.data)),
          player_color=str(escape(form.player_color.data)),
          first_player=str(escape(form.first_player.data)),
          opponent=str(escape(form.opponent.data))
        )
      )
    )
  else:
    response = make_response(
      render_template("input.html", form=form, result=None)
    )

  return response


@app.route(
  "/play/<k>/<player_color>/<first_player>/<opponent>/",
  methods=["GET", "POST"]
)
def Play(k=None, player_color=None, first_player=None, opponent=None):
  """Page for playing Connect-k."""
  ck = LoadGame()
  if not ck:
    # if there's ever a failure to load the game, go back to input page
    return redirect(url_for("Root"))

  # read inputs and set derived attributes if new game
  if (
    ck.k_                  is None
    and ck.player_color_   is None
    and ck.current_player_ is None
    and ck.opponent_       is None ):
    ck.k_ = int(k)
    ck.player_color_ = 0 if player_color == "Red" else 1
    ck.opponent_color_ = not ck.player_color_
    ck.current_player_ = ck.first_player_ = 0 if first_player == "Red" else 1
    ck.opponent_ = opponent
    if opponent.find("Computer") != -1:
      ck.computer_difficulty_ = opponent.split(" ")[-1][1:-1]

    ck.computer_is_thinking_ = (
      bool(
        opponent.find("Computer") != -1
        and ck.player_color_ != ck.current_player_
      )
    )

  # if computer opponent, it could be computer opponent's turn
  if ck.computer_is_thinking_:
    msg = (
      "<p><span style=\"color: {};\">"
        "Computer</span> is thinking..."
      "</p>"
    ).format("Crimson" if ck.current_player_ == 0 else "DarkBlue")
    response = make_response(
      render_template_string(
        BOARD_DISPLAY_TEMPLATE,
        ck=ck,
        msg=msg
      )
    )
    ck.computer_is_thinking_ = False
    mv = ck.ComputeMove_(ck.computer_difficulty_)
    ck.PlayMove_(mv)
    SaveGame(ck)
    return response

  # if computer moved, display move
  if (
    ck.current_player_ != ck.player_color_
    and ck.opponent_.find("Computer") != -1
  ):
    ck.UpdateDisplay_()
    SaveGame(ck)

  # go to input page if player clicks reset
  if "reset" in request.form:
    ck.ResetBoard_()
    SaveGame(ck)
    return redirect(url_for("Root"))

  # play the last requested move
  winner, opponent_winner = None, None
  if "move" in request.form:
    ck.PlayMove_(int(request.form["move"]))
    if ck.opponent_.find("Computer") != -1:
      ck.computer_is_thinking_ = True

  # check if the game is over for the player, opponent, and update board display
  winner, _ = ck.CheckForGameOver_(ck.player_color_)
  opponent_winner, _ = ck.CheckForGameOver_(ck.opponent_color_)
  ck.UpdateDisplay_()

  # the game could be over if anyone is a winner, and if both win it's a draw
  if winner or opponent_winner:
    if winner and opponent_winner:
      msg = "It's a draw!"
    else:
      winner = winner if winner else opponent_winner
      msg = (
        "<p><span style=\"color: {};\">"
          " Player {}</span> ({}) is the winner!"
        "</p>"
      ).format(
        "Crimson" if winner == "R"
        else "DarkBlue",
        winner,
        ck.opponent_ if winner == opponent_winner
        else "Human"
      )

    if ck.opponent_.find("Computer") != -1:
      ck.computer_is_thinking_ = False

  else:
    if (
      ck.current_player_ != ck.player_color_
      and ck.opponent_.find("Computer") != -1
    ):
      msg = (
        "<p><span style=\"color: {};\">"
          "Computer</span> is thinking..."
        "</p>"
      ).format("Crimson" if ck.current_player_ == 0 else "DarkBlue")
    else:
      msg = (
        "<p><span style=\"color: {};\">"
          "Player {}</span> it's your turn"
        "</p>"
      ).format(
        "Crimson" if ck.current_player_ == 0 else "DarkBlue",
        "R" if ck.current_player_ == 0 else "B"
      )

  response = make_response(
    render_template_string(
      BOARD_DISPLAY_TEMPLATE,
      ck=ck,
      msg=msg
    )
  )

  SaveGame(ck)
  return response


if __name__ == "__main__":
  app.run(host="127.0.0.1", port=8080, debug=True, threaded=False)

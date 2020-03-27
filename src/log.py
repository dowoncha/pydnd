import textwrap
import libtcodpy as libtcod

from constants import MSG_X, MSG_WIDTH, MSG_HEIGHT

game_msgs = []

def render_msgs(con):
  # render msgs
  y = 1
  for (line, color) in game_msgs:
    libtcod.console_set_default_foreground(con, color)
    libtcod.console_print_ex(con, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
    y += 1

def message(new_msg, color = libtcod.white):
  new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

  for line in new_msg_lines:
    # If the buffer is full, remove the first line to make rom for the new one
    if len(game_msgs) == MSG_HEIGHT:
      del game_msgs[0]

    # add the new line as a tuple, with tthe text and the color
    game_msgs.append((line, color))


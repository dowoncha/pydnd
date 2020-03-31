import libtcodpy as libtcod
import json
import textwrap
import queue
import logging
from datetime import datetime

from log import render_msgs, message
from collections import deque
from rect import Rect, Map 
from commands import AttackCommand, MoveCommand, KillCommand, SpawnCommand
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT, PANEL_HEIGHT, BAR_WIDTH, MS_PER_UPDATE

from world import World
def get_names_under_mouse():
  global mouse

  (x, y) = mouse.cx, mouse.cy

  # names = [obj.name for obj in objects if obj.x == x and obj.y == y and libtcod.map_is_in_fov(world.map)]

  return None

mouse = libtcod.Mouse()
key = libtcod.Key()

class Engine:
  def __init__(self):
  # Initialize libtcod root console
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python dnd', False, renderer=libtcod.RENDERER_OPENGL2)

    # Create our own main console
    self.con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

    self.panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

    # Create the world 
    world = World()

    world.populate_map()

    self.world = world

  def run(self):
    last_time = datetime.now()
    lag = 0.0

    # Main loop
    while not libtcod.console_is_window_closed():
      current_time = datetime.now()
      elapsed = current_time - last_time

      last_time = current_time
      lag += elapsed.microseconds

      # process input 
      libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

      # Get user input 
      exit = self.world.handle_keys()

      if exit:
        break
      
      while lag >= MS_PER_UPDATE:
        self.world.update(elapsed)
        lag -= MS_PER_UPDATE

      self.render()

      last_time = current_time

  def render(self):
    libtcod.console_set_default_foreground(0, libtcod.white)

    # draw the world
    self.world.render(self.con)

    # render gui
    libtcod.console_set_default_background(self.panel, libtcod.black)
    libtcod.console_clear(self.panel)

    render_msgs(self.panel)
    
    self.render_bar(self.con, 1, 1, BAR_WIDTH, 'HP', 90, 100, libtcod.light_red, libtcod.darker_red)
    
    # render names under mouse
    libtcod.console_set_default_foreground(self.panel, libtcod.light_gray)
    # libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())

    # Copy our console onto the root console 
    libtcod.console_blit(self.con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
    libtcod.console_blit(self.panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, SCREEN_HEIGHT - PANEL_HEIGHT)

    libtcod.console_flush()

    self.world.clear(self.con)

  def render_bar(self, con, x, y, total_width, name, value, max, fg, bg):
    bar_width = int(float(value) / max * total_width)

    libtcod.console_set_default_background(con, bg)
    libtcod.console_rect(con, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_foreground(con, fg)

    libtcod.console_set_default_background(con, bg)
    if bar_width > 0:
      libtcod.console_rect(con, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    # Text
    libtcod.console_set_default_foreground(con, libtcod.white)
    libtcod.console_print_ex(con, int(x + total_width / 2), y, libtcod.BKGND_NONE, libtcod.CENTER, name + ': ' + str(value) + '/' + str(max))

def main():
  engine = Engine()

  engine.run()

if __name__ == "__main__":
  main()
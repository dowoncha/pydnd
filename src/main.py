import libtcodpy as libtcod
import json
import textwrap
import queue
import logging
from datetime import datetime
import time
from typing import Dict

import tcod.event
import tcod.console

from log import render_msgs, message
from collections import deque
from rect import Rect, Map 
from commands import Command, AttackCommand, MoveCommand, WalkCmd, KillCommand, SpawnCommand, PrintCmd
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT, PANEL_HEIGHT, BAR_WIDTH, MS_PER_UPDATE, UPDATE_PER_FRAME_LIMIT
from tcod import event

from world import World

def time_in_millis():
  return int(round(time.time() * 1000))

class GameTime:
  def __init__(self):
    self.clock = 0
    self.last_actual = 0
    self.next_update = 0

class CommandManager:
  def __init__(self):
    self.bindings: Dict[int, Command] = {
      tcod.event.K_c: PrintCmd("Toggle character sheet"),
      tcod.event.K_UP: WalkCmd(id = "player", dx = 0, dy = -1),
      tcod.event.K_DOWN: WalkCmd(id = "player", dx = 0, dy = 1),
      tcod.event.K_RIGHT: WalkCmd(id = "player", dx = 1, dy = 0),
      tcod.event.K_LEFT: WalkCmd(id = "player", dx = -1, dy = 0)
    }

  def get_command(self, key: int) -> Command:
    return self.bindings.get(key)

  def bind_command(self, key: int, command: Command):
    self.bindings[key] = command

class Engine:
  def __init__(self):
    # Initialize libtcod root console
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    self.root = libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python dnd', False, renderer=libtcod.RENDERER_OPENGL2)

    # Create our own main console
    self.con = tcod.console.Console(SCREEN_WIDTH, SCREEN_HEIGHT)

    self.panel = tcod.console.Console(SCREEN_WIDTH, PANEL_HEIGHT)

    # Create the world 
    world = World()

    world.populate_map()

    self.world = world

    self.game_time = GameTime()

    self.command_manager = CommandManager()

  def run(self):
    # Main loop
    while not libtcod.console_is_window_closed():
      current_time = time_in_millis()

      if current_time - self.game_time.last_actual > MS_PER_UPDATE * UPDATE_PER_FRAME_LIMIT:
        self.game_time.clock += (MS_PER_UPDATE * UPDATE_PER_FRAME_LIMIT)
      else:
        self.game_time.clock += (current_time - self.game_time.last_actual)

      while self.game_time.clock >= self.game_time.next_update:
        self.time_elapsed = MS_PER_UPDATE
        self.time_current = self.game_time.next_update

        self.update()

        self.game_time.next_update += MS_PER_UPDATE

      self.game_time.last_actual = time_in_millis()

      self.render()

      # Handle input
      for event in tcod.event.get():
        if event.type == "KEYDOWN":
          # Key escape
          if event.sym == 27:
            raise SystemExit()
          else:
            self.check_command(event)
        elif event.type == "MOUSEBUTTONDOWN":
          pass
        elif event.type == "MOUSEMOTION":
          self.mouse = event

  def render(self):
    self.root.default_fg = (255, 255, 255)

    # draw the world
    self.world.render(self.con)

    # render gui
    self.panel.default_bg = libtcod.black
    self.panel.clear()

    render_msgs(self.panel)
    
    self.render_bar(self.con, 1, 1, BAR_WIDTH, 'HP', 90, 100, libtcod.light_red, libtcod.darker_red)
    
    # render names under mouse
    libtcod.console_set_default_foreground(self.panel, libtcod.light_gray)
    # libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())

    # Copy our console onto the root console 
    self.con.blit(self.root, 0, 0, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
    self.panel.blit(self.root, 0, SCREEN_HEIGHT - PANEL_HEIGHT, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT) # 0, 0, 

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

  def check_command(self, key_event: tcod.event.KeyboardEvent):
    # key = libtcod.console_wait_for_keypress(True)
    # if key.vk == libtcod.KEY_ENTER and key.lalt:
    #   libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    # elif key.vk == libtcod.KEY_ESCAPE:
    #   return True
    
    # player = self.get_player()

    # if player:
    #   new_x = player.x
    #   new_y = player.y

    #   if libtcod.console_is_key_pressed(libtcod.KEY_UP):
    #     new_y -= 1
    #   elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
    #     new_y += 1
    #   elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
    #     new_x -= 1
    #   elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
    #     new_x += 1
      
    #   self.send_command(MoveCommand(player, new_x, new_y))

    if key_event.sym:
      command = self.command_manager.get_command(key_event.sym)

      if command is not None:
        self.world.send_command(command)

  def update(self):
    # print('clock', self.game_time.clock)
    # print(self.game_time.last_actual)
    # print(self.game_time.next_update)
    # print(self.time_elapsed)
    # print(self.time_current)

    self.world.update()

def main():
  engine = Engine()

  engine.run()

if __name__ == "__main__":
  main()
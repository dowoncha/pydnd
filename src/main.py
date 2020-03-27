import libtcodpy as libtcod
import json
import textwrap
import queue
import logging
from datetime import datetime

from log import render_msgs, message
from collections import deque
from rect import Rect, Map 
from commands import AttackCommand, MoveCommand, KillCommand
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT, PANEL_HEIGHT, BAR_WIDTH, MS_PER_UPDATE

class GameObject:
  id_counter = 1

  def __init__(
    self, 
    x, 
    y, 
    id = None, 
    name = "game_object", 
    char = None, 
    color = None, 
    prototype = None, 
    blocks = False, 
    hp = None
  ):
    self.id = id or ++GameObject.id_counter
    self.x = int(x)
    self.y = int(y)
    self.name = name
    self.blocks = blocks

    self.max_hp = hp
    self.hp = hp

    if char is not None:
      self.char = char
    elif prototype and prototype.get('char'):
      self.char = prototype.get('char')
    else:
      self.char = ' '

    if color is not None:
      self.color = color
    elif prototype and prototype.get('color'):
      self.color = prototype.get('color')
    else:
      self.color = [0, 0, 0]

    self.prototype = prototype

  def add_component(self, component):
    self.components.append(component)

  def set_position(self, x, y):
    self.x = x
    self.y = y

  def move(self, dx, dy):
    self.x += dx
    self.y += dy

  def draw(self, console):
    libtcod.console_set_default_foreground(console, self.color)
    libtcod.console_put_char(console, int(self.x), int(self.y), self.char, libtcod.BKGND_NONE)
  
  def clear(self, con) :
    libtcod.console_put_char(con, int(self.x), int(self.y), ' ', libtcod.BKGND_NONE)

  def apply_damage(self, damage):
    if self.hp is not None:
      self.hp -= damage

      if self.hp < 0:
        return True

    return False

class World:
  def __init__(self):
    self.game_map = Map(MAP_WIDTH, MAP_HEIGHT)
    start_room = self.game_map.rooms[0]

    playerx = start_room.w / 2 + start_room.x1
    playery = start_room.h / 2 + start_room.y1

    player = GameObject(
      playerx, 
      playery, 
      id = "player",
      name = "Gromash the Corpse-Eater", 
      char = '@', 
      color = libtcod.white,
      blocks = True,
      hp = 100,
    )

    npc = GameObject(
      playerx, 
      playery + 2, 
      name = "commoner", 
      char = 'c', 
      color = libtcod.yellow,
      blocks = True,
      hp = 10
      )

    self.load_assets()

    # goblin_room = self.get_map().get_room(0)

    # goblinx = goblin_room.x1 + goblin_room.w / 2
    # gobliny = goblin_room.y1 + goblin_room.h / 2

    # self.spawn_game_object("m_goblin_grunt", goblinx, gobliny, blocks = True)

    self.objects = [npc, player]
    
    self.commands = deque()

  def is_blocked(self, x, y):
    if self.game_map.get_tile(x, y).blocked:
      return True

    for object in self.objects:
      if object.blocks and object.x == x and object.y == y:
        return True
    
    return False

  def get_map(self):
    return self.game_map

  def spawn_game_object(self, id, x, y, blocks = False):
    prototype = self.get_prototype(id)

    if prototype is None:
      return

    object = GameObject(x, y, name = id, prototype = prototype, blocks = blocks)

    self.objects.append(object)

  def get_prototype(self, id):
    asset = self.library.get(id)

    if asset is None:
      return None
    
    prototype_id = asset.get('prototype')

    while prototype_id is not None:
      prototype = self.library[prototype_id] 

      for key, value in prototype.items():
        if asset[key] is None:
          asset[key] = value

      if prototype.prototype:
        prototype_id = prototype.prototype
      else:
        prototype_id = None

    return asset

  def load_assets(self):
    self.library = {}

    with open('assets/races.json') as f:
      races = json.load(f)
      for race in races:
        self.library[race.get('id')] = race

    with open('assets/monsters.json') as f:
      monsters = json.load(f)
      for m in monsters:
        self.library[m.get('id')] = m

  def get_player(self):
    return [object for object in self.objects if object.id == "player"][0]

  def render(self, console):
    for object in self.objects:
      object.draw(console)

    self.game_map.render(console)

  def clear(self, console):
    for object in self.objects:
      object.clear(console)

  def update(self):
    if len(self.commands) > 0:
      command = self.commands.popleft()

      print('processing ', str(command))

      command.execute(self)

  def handle_keys(self):
    key = libtcod.console_wait_for_keypress(True)
    if key.vk == libtcod.KEY_ENTER and key.lalt:
      libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
      return True
    
    player = self.get_player()

    if player:
      new_x = player.x
      new_y = player.y

      if libtcod.console_is_key_pressed(libtcod.KEY_UP):
        new_y -= 1
      elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
        new_y += 1
      elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
        new_x -= 1
      elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
        new_x += 1
      
      self.send_command(MoveCommand(player, new_x, new_y))

  def send_command(self, command):
    self.commands.append(command)

  def remove_object(self, object):
    self.objects = [o for o in self.objects if not o.id == object.id]

  def search(self, x, y):
    for object in self.objects:
      if object.x == x and object.y == y:
        return object

    return None

def render_bar(con, x, y, total_width, name, value, max, fg, bg):
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

def render(world, con, panel):
  libtcod.console_set_default_foreground(0, libtcod.white)

  # draw the world
  world.render(con)

  # render gui
  libtcod.console_set_default_background(panel, libtcod.black)
  libtcod.console_clear(panel)

  render_msgs(panel)
  
  render_bar(con, 1, 1, BAR_WIDTH, 'HP', 90, 100, libtcod.light_red, libtcod.darker_red)
  
  # render names under mouse
  libtcod.console_set_default_foreground(panel, libtcod.light_gray)
  # libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())

  # Copy our console onto the root console 
  libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
  libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, SCREEN_HEIGHT - PANEL_HEIGHT)

  libtcod.console_flush()

  world.clear(con)

def get_names_under_mouse():
  global mouse

  (x, y) = mouse.cx, mouse.cy

  # names = [obj.name for obj in objects if obj.x == x and obj.y == y and libtcod.map_is_in_fov(world.map)]

  return None

mouse = libtcod.Mouse()
key = libtcod.Key()

def main():
  # Initialize libtcod root console
  libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
  libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python dnd', False, renderer=libtcod.RENDERER_OPENGL2)

  # Create our own main console
  con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

  panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

  # Create the world 
  world = World()

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
    exit = world.handle_keys()

    if exit:
      break
    

    while lag >= MS_PER_UPDATE:
      world.update()
      lag -= MS_PER_UPDATE

    render(world, con, panel)

    last_time = current_time

if __name__ == "__main__":
  main()
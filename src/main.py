import libtcodpy as libtcod
import textwrap
import json
import queue
from rect import Rect, Map 

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 43
PANEL_HEIGHT = 7
LIMIT_FPS = 20

MAP_WIDTH = 80
MAP_HEIGHT = 43

BAR_WIDTH = 20

color_dark_wall = libtcod.Color(0, 0, 100)
color_dark_ground = libtcod.Color(50, 50, 150)

class GameObject:
  def __init__(self, x, y, name = "game_object", char = None, color = None, prototype = None, blocks = False):
    self.x = int(x)
    self.y = int(y)
    self.name = name
    self.blocks = blocks

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

  def move(self, dx, dy):
    self.x += dx
    self.y += dy

  def draw(self, console):
    libtcod.console_set_default_foreground(console, self.color)
    libtcod.console_put_char(console, int(self.x), int(self.y), self.char, libtcod.BKGND_NONE)
  
  def clear(self, con) :
    libtcod.console_put_char(con, int(self.x), int(self.y), ' ', libtcod.BKGND_NONE)

class Character:
  def __init__(self, race, g_class):
    self.race = race
    self.g_class = g_class

class Fighter:
  def __init__(self, hp):
    self.max_hp = hp
    self.hp = hp

class World:
  def __init__(self):
    game_map = Map(MAP_WIDTH, MAP_HEIGHT)
    start_room = game_map.rooms[0]

    playerx = start_room.w / 2 + start_room.x1
    playery = start_room.h / 2 + start_room.y1

    player = GameObject(
      playerx, 
      playery, 
      name = "Gromash the Corpse-Eater", 
      char = '@', 
      color = libtcod.white,
      blocks = True
    )
    npc = GameObject(
      playerx, 
      playery + 2, 
      name = "commoner", 
      char = 'c', 
      color = libtcod.yellow,
      blocks = True
      )

    self.load_assets()

    self.objects = [npc, player]
    self.game_map = game_map

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

    print("spawning ", id)

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
    return self.objects[1]

  def render(self, console):
    for object in self.objects:
      object.draw(console)

    self.game_map.render(console)

  def clear(self, console):
    for object in self.objects:
      object.clear(console)

  def update(self):
    pass

  def handle_keys(self):
    key = libtcod.console_wait_for_keypress(True)
    if key.vk == libtcod.KEY_ENTER and key.lalt:
      libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
      return True
    
    player = self.get_player()

    if libtcod.console_is_key_pressed(libtcod.KEY_UP):
      if not self.is_blocked(int(player.x), int(player.y - 1)):
        player.move(0, -1)
    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
      if not self.is_blocked(int(player.x), int(player.y + 1)):
        player.move(0, 1)
    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
      if not self.is_blocked(int(player.x - 1), int(player.y)):
        player.move(-1, 0)
    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
      if not self.is_blocked(int(player.x + 1), int(player.y)):
        player.move(1, 0)

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

MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

game_msgs = []

def message(new_msg, color = libtcod.white):
  new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

  for line in new_msg_lines:
    # If the buffer is full, remove the first line to make rom for the new one
    if len(game_msgs) == MSG_HEIGHT:
      del game_msgs[0]

    # add the new line as a tuple, with tthe text and the color
    game_msgs.append((line, color))

def render(world, con, panel):
  libtcod.console_set_default_foreground(0, libtcod.white)

  # draw the world
  world.render(con)

  # render gui
  libtcod.console_set_default_background(panel, libtcod.black)
  libtcod.console_clear(panel)

  # render msgs
  y = 1
  for (line, color) in game_msgs:
    libtcod.console_set_default_foreground(panel, color)
    libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
    y += 1
  
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

  message("Welcome stranger! Prepare to perish in the dungeon", libtcod.red)

  # Create the world 
  world = World()

  goblin_room = world.get_map().get_room(1)

  goblinx = goblin_room.x1 + goblin_room.w / 2
  gobliny = goblin_room.y1 + goblin_room.h / 2

  world.spawn_game_object("m_goblin_grunt", goblinx, gobliny, blocks = True)
  
  # Main loop
  while not libtcod.console_is_window_closed():
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
    
    render(world, con, panel)

    # Get user input 
    exit = world.handle_keys()

    if exit:
      break

    world.update()

if __name__ == "__main__":
  main()
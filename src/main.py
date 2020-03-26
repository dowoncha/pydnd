import libtcodpy as libtcod
import json

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 45
PANEL_HEIGHT = 7
LIMIT_FPS = 20

MAP_WIDTH = 80
MAP_HEIGHT = 43

color_dark_wall = libtcod.Color(0, 0, 100)
color_dark_ground = libtcod.Color(50, 50, 150)

class GameObject:
  def __init__(self, x, y, char = None, color = None, prototype = None, components = []):
    self.x = x
    self.y = y

    if char is not None:
      self.char = char
    elif prototype.get('char'):
      self.char = prototype.get('char')
    else:
      self.char = ' '

    if color is not None:
      self.color = color
    elif prototype.get('color'):
      self.color = prototype.get('color')
    else:
      self.color = [0, 0, 0]

    self.prototype = prototype
    self.components = components

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

class Tile:
  def __init__(self, blocked, block_sight = None):
    self.blocked = blocked

    if block_sight is None: 
      block_sight = blocked

    self.block_sight = block_sight

class Map:
  def __init__(self, tiles = None):
    if tiles is None:
      tiles = [[ Tile(False)
        for y in range(MAP_HEIGHT) ]
          for x in range(MAP_WIDTH) ]

      tiles[30][22].blocked = True
      tiles[30][22].block_sight = True
      tiles[50][22].blocked = True
      tiles[50][22].blocked = True

    self.tiles = tiles

  def render(self, con):
    for y in range(MAP_HEIGHT):
      for x in range(MAP_WIDTH):
        wall = self.tiles[x][y].block_sight
        if wall: 
          libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
        else:
          libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)

class World:
  def __init__(self):
    player = GameObject(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, '@', libtcod.white)
    npc = GameObject(SCREEN_WIDTH / 2 - 5, SCREEN_HEIGHT / 2, 't', libtcod.yellow)
    game_map = Map()

    self.load_assets()

    self.objects = [npc, player]
    self.game_map = game_map

  def spawn_game_object(self, id, x, y):
    prototype = self.get_prototype(id)

    if prototype is None:
      return

    object = GameObject(x, y, prototype = prototype)

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

def handle_keys(object):
  key = libtcod.console_wait_for_keypress(True)
  if key.vk == libtcod.KEY_ENTER and key.lalt:
    libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
  elif key.vk == libtcod.KEY_ESCAPE:
    return True

  if libtcod.console_is_key_pressed(libtcod.KEY_UP):
    object.move(0, -1)
  elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
    object.move(0, 1)
  elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
    object.move(-1, 0)
  elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
    object.move(1, 0)

def render_bar(con, x, y, total_width, name, value, max, fg, bg):
  bar_width = int(float(value) / max * total_width)

  libtcod.console_set_default_background(con, bg)
  libtcod.console_rect(con, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

  libtcod.console_set_default_background(con, fg)

  libtcod.console_set_default_background(con, bg)
  if bar_width > 0:
    libtcod.console_rect(con, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

  # Text
  libtcod.console_set_default_foreground(con, libtcod.white)
  libtcod.console_print_ex(con, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER, name + ': ' + str(value) + '/' + str(max))

def main():
  # Initialize libtcod root console
  # libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
  libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python dnd', False, renderer=libtcod.RENDERER_SDL2)

  # Create our own main console
  con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

  panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

  # Create the world 
  world = World()

  world.spawn_game_object("m_goblin_grunt", SCREEN_WIDTH / 2 + 5, SCREEN_HEIGHT / 2)

  # Main loop
  while not libtcod.console_is_window_closed():
    libtcod.console_set_default_foreground(0, libtcod.white)

    # draw the world
    world.render(con)

    # render gui
    # libtcod.console_set_default_background(panel, libtcod.black)
    # libtcod.console_clear(panel)

    # render_bar(1, 1, 20, 'HP', world.get_player().hp, world.get_player().max_hp, libtcod.light_red, libtcod.darker_red)

    # Copy our console onto the root console 
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, SCREEN_HEIGHT - PANEL_HEIGHT)

    libtcod.console_flush()

    world.clear(con)

    # Get user input 
    exit = handle_keys(world.get_player())
    
    if exit:
      break

if __name__ == "__main__":
  main()
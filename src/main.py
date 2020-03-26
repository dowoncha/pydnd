import libtcodpy as libtcod
import json

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 45
LIMIT_FPS = 20

MAP_WIDTH = 80
MAP_HEIGHT = 45

color_dark_wall = libtcod.Color(0, 0, 100)
color_dark_ground = libtcod.Color(50, 50, 150)

class GameObject:
  def __init__(self, x, y, char = None, color = None, prototype = None):
    self.x = x
    self.y = y


    print(prototype)

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

  def move(self, dx, dy):
    self.x += dx
    self.y += dy

  def draw(self, console):
    libtcod.console_set_default_foreground(console, self.color)
    libtcod.console_put_char(console, int(self.x), int(self.y), self.char, libtcod.BKGND_NONE)
  
  def clear(self, con) :
    libtcod.console_put_char(con, int(self.x), int(self.y), ' ', libtcod.BKGND_NONE)

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
  
def main():
  # libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
  libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python dnd', False, renderer=libtcod.RENDERER_SDL2)

  con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
  
  world = World()

  world.spawn_game_object("m_goblin_grunt", SCREEN_WIDTH / 2 + 5, SCREEN_HEIGHT / 2)

  while not libtcod.console_is_window_closed():
    libtcod.console_set_default_foreground(0, libtcod.white)

    world.render(con)
    
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    libtcod.console_flush()

    world.clear(con)
    
    exit = handle_keys(world.get_player())
    
    if exit:
      break

if __name__ == "__main__":
  main()
import libtcodpy as libtcod
color_dark_wall = libtcod.Color(0, 0, 100)
color_dark_ground = libtcod.Color(50, 50, 150)

class Rect:
    #a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w 
        self.y2 = y + h
        self.w = w
        self.h = h

def create_room(game_map, room):
    #go through the times in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 +1, room.y2):
            game_map[x][y].blocked = False
            game_map[x][y].block_sight = False

class Tile:
  def __init__(self, blocked, block_sight = None):
    self.blocked = blocked

    if block_sight is None: 
      block_sight = blocked

    self.block_sight = block_sight

class Map:
  def __init__(self, width, height, tiles = None):
    if tiles is None:
      self.make_map(width, height)
    else:
      self.tiles = tiles

    self.width = width
    self.height = height

  def make_map(self, width, height):
    #filll map with "blocked" tiles
    self.tiles = [[ Tile(True)
    for y in range(height) ]
        for x in range(width) ]

    #create two rooms
    room1 = Rect(20, 15, 10, 15)
    room2 = Rect(50, 15, 10, 15)
    create_room(self.tiles, room1)
    create_room(self.tiles, room2)
    create_h_tunnel(self.tiles, 25, 55, 23)

    self.rooms = [room1, room2]


  def render(self, con):
    for y in range(self.height):
      for x in range(self.width):
        wall = self.tiles[x][y].block_sight
        if wall: 
          libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
        else:
          libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)

def create_h_tunnel(game_map, x1, x2, y):
  for x in range(min(x2, x1), max(x2,x1) + 1):
    game_map[x][y].blocked = False
    game_map[x][y].block_sight = False


def create_v_tunnel(game_map, y1, y2, x):
  #verticle tunnel
  for y in range(min(y1,y2), max(y1, y2) + 1):
    game_map[x][y].blocked = False
    game_map[x][y].blocked_sight = False


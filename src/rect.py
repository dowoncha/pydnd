import libtcodpy as libtcod
import tcod.console

color_dark_wall = libtcod.Color(0, 0, 100)
color_dark_ground = libtcod.Color(50, 50, 150)

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

class Rect:
    # a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
        self.w = w
        self.h = h

    def center(self):
      center_x = (self.x1 + self.x2) / 2
      center_y = (self.y1 + self.y2) / 2
      return (center_x, center_y)

    def intersect(self, other):
      # returns true if this rectangle intersects with another one
      return (self.x1 <= other.x2 and self.x2 > + other.x1 and
              self.y1 <= other.y2 and self.y2 >= other.y1)

class Tile:
  def __init__(self, blocked, block_sight=None):
    self.blocked = blocked

    if block_sight is None:
      block_sight = blocked

    self.block_sight = block_sight

class Cell:
	def __init__(self, tile, prop, entity, item):
		self.tile = tile
		self.prop = prop
		self.entity = entity
		self.item = item

class Map:
	def __init__(self, width, height, tiles=None):
		if tiles is None:
			self.make_map(width, height)
		else:
			self.tiles = tiles

		self.width = width
		self.height = height

	def create_room(self, room):
		# go through the times in the rectangle and make them passable
		for x in range(room.x1 + 1, room.x2):
			for y in range(room.y1 + 1, room.y2):
				self.tiles[x][y].blocked = False
				self.tiles[x][y].block_sight = False

	def dun_maker(self, width, height):
		rooms = []
		num_rooms = 0

		for r in range(MAX_ROOMS):
			# random width and height
			w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
			h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
			# random position without going out of the boundaries of the map
			x = libtcod.random_get_int(0, 0, width - w - 1)
			y = libtcod.random_get_int(0, 0, height - h - 1)

			# "Rect" class makes rectangles easier to work
			new_room = Rect(x, y, w, h)

			# run through the other room and see if they intersect with this one
			failed = False
			for other_room in rooms:
				if new_room.intersect(other_room):
					failed = True
					break

			if not failed:
				# this means there are no intersections, so this room is valid

				# "paint" it to the map's tiles
				self.create_room(new_room)

				# center coordinates of new room, will be useful later
				(new_x, new_y) = new_room.center()
				
				if num_rooms > 0:
					# all rooms after the first:
					# connect it to the previous room with a tunnel

					# center coordinates of previous room
					(prev_x, prev_y) = rooms[num_rooms-1].center()

					# draw a coin (random number that is either 0 or 1)
					if libtcod.random_get_int(0, 0, 1) == 1:
						self.create_h_tunnel(prev_x, new_x, prev_y)
						self.create_v_tunnel(prev_y, new_y, new_x)
					else:
						# first move vertically, then horizontally
						self.create_v_tunnel(prev_y, new_y, prev_x)
						self.create_h_tunnel(prev_x, new_x, new_y)

				# finally, append the new room to the lis
				rooms.append(new_room)
				num_rooms += 1
	
		self.rooms = rooms 

	def get_room(self, id):
		return self.rooms[id]

	def make_map(self, width, height):
		# filll map with "blocked" tiles
		self.tiles = [[ Tile(True)
		for y in range(height) ]
			for x in range(width) ]

		self.dun_maker(width, height)

	def get_tile(self, x, y):
		return self.tiles[x][y]

	def render(self, console: tcod.console.Console):
		for y in range(self.height):
			for x in range(self.width):
				wall = self.tiles[x][y].block_sight
				if wall: 
					libtcod.console_set_char_background(console, x, y, color_dark_wall, libtcod.BKGND_SET)
				else:
					libtcod.console_set_char_background(console, x, y, color_dark_ground, libtcod.BKGND_SET)

	def create_h_tunnel(self, x1, x2, y):
  		for x in range(int(min(x2, x1)), int(max(x2,x1) + 1)):
			  self.tiles[int(x)][int(y)].blocked = False
			  self.tiles[int(x)][int(y)].block_sight = False

	def create_v_tunnel(self, y1, y2, x):
		# verticle tunnel
		for y in range(int(min(y1,y2)), int(max(y1, y2) + 1)):
			self.tiles[int(x)][int(y)].blocked = False
			self.tiles[int(x)][int(y)].block_sight = False


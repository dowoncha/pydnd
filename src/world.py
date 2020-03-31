from collections import deque
from datetime import datetime
import libtcodpy as libtcod
import json

from log import message
from constants import MAP_WIDTH, MAP_HEIGHT
from game_object import GameObject
from rect import Map
from time_schedule import TimeSchedule
from commands import SpawnCommand, MoveCommand

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

    self.objects = [npc, player]
    self.commands = deque()
    self.commands_history = []
    self.game_time = datetime.now()

    self.scheduler = TimeSchedule()

    self.turns = 0
    self.turnsTaken = {}

  def populate_map(self):
    goblin = self.get_prototype('m_goblin_grunt')

    if goblin is None:
      return

    for room in self.get_map().rooms:
      x = room.x1 + room.w / 2
      y = room.y1 + room.h / 2

      self.send_command(SpawnCommand(goblin, x, y))

  def is_blocked(self, x, y):
    if self.game_map.get_tile(x, y).blocked:
      return True

    for object in self.objects:
      if object.blocks and object.x == x and object.y == y:
        return True
    
    return False

  def get_map(self):
    return self.game_map

  def spawn_game_object(self, id = None, prototype = None, x = 0, y = 0):
    object = GameObject(x, y, id = id)

    self.objects.append(object)

    print("Spawned object w id " + object.id)

    return object.id

  def get_prototype(self, id):
    """
    """
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

  def update(self, elapsed):
    if len(self.commands) > 0:
      command = self.commands.popleft()

      command.execute(self)

      self.commands_history.append(command)

    # for object in self.objects:
    #   self.scheduler.schedule_event(object, object.action_delay())
    #   self.turns += object.speed
    #   self.turnsTaken[object] = 0

    # self.turns *= 3

    # while self.turns > 0:
    #   object = self.scheduler.next_event()
    #   self.turnsTaken[object] += 1
    #   print( object)
    #   self.turns -= 1

    #   self.scheduler.schedule_event(object, object.action_delay())


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

  def kill(self, target):
    target.on_death(self)

    message(target.name + " has died")

    self.remove_object(target)

  def remove_object(self, object):
    print("Removing objects with id " + str(object.id))

    self.objects = [o for o in self.objects if not o.id == object.id]

  def search(self, x, y):
    for object in self.objects:
      if object.x == x and object.y == y:
        return object

    return None


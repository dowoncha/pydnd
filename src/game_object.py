import libtcodpy as libtcod
import tcod.color
import tcod.console
from typing import List, Tuple

class Item:
  pass

class GameObject:
  id_counter = 1

  BASE_TIME = 10.0

  def __init__(
    self, 
    x: int = 0, 
    y: int = 0, 
    id: str = None, 
    name: str = "game_object", 
    char: int = ord(' '), 
    color: Tuple[int, int, int] = [0, 0, 0], 
    prototype = None, 
    blocks: bool = False, 
    hp: int = None,
    speed: int = 1,
    inventory: List[Item] = []
  ):
    GameObject.id_counter += 1

    if id is None:
      self.id = str(GameObject.id_counter)
    else:
      self.id = str(id)

    self.x = int(x)
    self.y = int(y)
    # self.prototype = prototype
    self.name = name
    self.blocks = blocks

    self.max_hp = hp 
    self.hp = self.max_hp

    self.char = ord(char) if type(char) is str else char

    self.color = color

    self.speed = speed
    self.prototype = prototype
    self.inventory = inventory

  @property
  def blocks(self) -> bool:
    return self.__blocks # or self.prototype.get('blocks')

  @blocks.setter
  def blocks(self, blocks: bool):
    self.__blocks = blocks
    # if self.prototype:
    #   self.prototype['blocks'] = blocks

  def set_position(self, x: int, y: int):
    self.x = x
    self.y = y

  def move(self, dx: int, dy: int):
    self.x += dx
    self.y += dy

  def render(self, console: tcod.console.Console):
    console.default_fg = self.color
    console.put_char(int(self.x), int(self.y), int(self.char))
  
  def clear(self, console: tcod.console.Console):
    libtcod.console_put_char(console, int(self.x), int(self.y), ' ', libtcod.BKGND_NONE)

  def apply_damage(self, damage: int) -> bool:
    if self.hp is not None:
      self.hp -= damage

      if self.hp < 0:
        return True

    return False

  def action_delay(self):
    return GameObject.BASE_TIME / self.speed
  
  def on_death(self, world):
    pass

import libtcodpy as libtcod

class GameObject:
  id_counter = 1

  BASE_TIME = 10.0

  def __init__(
    self, 
    x, 
    y, 
    id = None, 
    name = "game_object", 
    char = None, 
    color = None, 
    # prototype = None, 
    blocks = False, 
    hp = None,
    speed = 1
  ):
    if id is None:
      self.id = str(++self.id_counter)
    else:
      self.id = str(id)
    self.x = int(x)
    self.y = int(y)
    # self.prototype = prototype
    self.name = name
    self.blocks = blocks

    self.max_hp = hp # or self.prototype.get('min_health')
    self.hp = self.max_hp

    if char is not None:
      self.char = char
    # elif prototype and prototype.get('char'):
      # self.char = prototype.get('char')
    else:
      self.char = ' '

    if color is not None:
      self.color = color
    # elif prototype and prototype.get('color'):
      # self.color = prototype.get('color')
    else:
      self.color = [0, 0, 0]

    self.speed = speed
    self.components = []

  def add_component(self, component):
    self.components.append(component)

  @property
  def x(self):
    return self.__x

  @x.setter
  def x(self, x):
    self.__x = x

  @property
  def blocks(self):
    return self.__blocks # or self.prototype.get('blocks')

  @blocks.setter
  def blocks(self, blocks):
    self.__blocks = blocks
    # if self.prototype:
    #   self.prototype['blocks'] = blocks

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

  def action_delay(self):
    return GameObject.BASE_TIME / self.speed
  
  def on_death(self, world):
    pass


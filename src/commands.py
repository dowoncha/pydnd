from log import message

class Command:
  def execute(self, world):
    pass

class MoveCommand(Command):
  def __init__(self, target, x, y):
    self.target = target
    self.x = x
    self.y = y

  def execute(self, world):
    if self.target:
      if not world.is_blocked(self.x, self.y):
        self.target.set_position(self.x, self.y)
      else:
        collider = world.search(self.x, self.y)
        if collider:
          world.send_command(AttackCommand(self.target, collider))

class WalkCmd(Command):
  def __init__(self, id: str, dx: int, dy: int):
    self.id = id
    self.dx = dx
    self.dy = dy

  def execute(self, world):
    if self.id:
      target = world.get_object_id(self.id)

      if target is not None:
        new_x = target.x + self.dx
        new_y = target.y + self.dy

        if not world.is_blocked(new_x, new_y):
          target.set_position(new_x, new_y)
        else:
          collider = world.search(new_x, new_y)
          
          if collider:
            world.send_command(AttackCommand(target, collider))


class SpawnCommand(Command):
  def __init__(self, prototype, x: int, y: int):
    self.prototype = prototype
    self.x = x
    self.y = y

  def execute(self, world):
    id = world.spawn_game_object(
      prototype = self.prototype, 
      x = self.x, 
      y = self.y)

    message("Spawned " + str(id))

class AttackCommand(Command):
  def __init__(self, attacker, target):
    self.attacker = attacker
    self.target = target

  def execute(self, world):
    if self.target and self.target.hp:
      damage = 5
      self.target.apply_damage(damage)

      if self.target.hp <= 0:
        world.send_command(KillCommand(self.target))

      message(self.target.name + " was damaged for " + str(damage) + " hp")

class KillCommand(Command):
  def __init__(self, target):
    self.target = target

  def execute(self, world):
    if self.target and self.target.hp <= 0:
      world.kill(self.target)

class PrintCmd(Command):
  def __init__(self, msg):
    self.msg = msg
  
  def execute(self, world):
    message(self.msg)
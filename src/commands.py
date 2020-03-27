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

class AttackCommand(Command):
  def __init__(self, attacker, target):
    self.attacker = attacker
    self.target = target

  def execute(self, world):
    if self.target:
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
      world.remove_object(self.target)

      message(self.target.name + " has died")


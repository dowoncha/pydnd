from priority_queue import PriorityQueue

class TimeSchedule:
  def __init__(self):
    self.scheduled_events = PriorityQueue()

  def schedule_event(self, event, delay = 0.0):
    if event is not None:
      self.scheduled_events.enqueue(event, delay)

  def next_event(self):
    time, event = self.scheduled_events.dequeue_with_key()
    self.scheduled_events.adjust_priorities(-time)

    return event

  def cancel_event(self, event):
    self.scheduled_events.erase_ref(event)


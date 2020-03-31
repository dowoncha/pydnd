class PriorityQueue:
    def __init__(self):
        self.__queue = []

    def __len__(self):
        return len(self.__queue)

    def enqueue(self, value, priority = 0.0):
        """
            Append a new element to the queue
            according to its priority.
        """

        tuple = [priority, value]

        # Insert the tuple in sorted position in the queue.  If a
        # tuple with equal priority is encountered, the new tuple is
        # inserted after it.

        finalPos = 0
        high = len(self)
        while finalPos < high:
            middle = (finalPos + high) // 2
            if tuple[0] < self.__queue[middle][0]:
                high = middle
            else:
                finalPos = middle + 1

        self.__queue.insert(finalPos, tuple)

    def adjust_priorities(self, add):
        """
            Increases all priorities.
        """

        for v in self.__queue:
            v[0] += add

    def dequeue(self):
        """
            Pop the value with the lowest priority.
        """

        return self.__queue.pop(0)[1]

    def dequeue_with_key(self):
        """
            Pop the (priority, value) tuple with the lowest priority.
        """

        return self.__queue.pop(0)

    def erase(self, value):
        """
            Removes an element from the queue by value.
        """

        self.__erase(value, lambda a, b: a == b)

    def erase_ref(self, value):
        """
            Removes an element from the queue by reference.
        """

        self.__erase(value, lambda a, b: a is b)

    def __erase(self, value, test):
        """
            All tupples t are removed from the queue
            if test(t[1], value) evaluates to True.
        """

        i = 0
        while i < len(self.__queue):
            if test(self.__queue[i][1], value):
                del self.__queue[i]
            else:
                i += 1

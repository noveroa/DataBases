'''
The queue abstract data type is defined by the following structure and operations. A queue is structured, as described above, as an ordered collection of items which are added at one end, called the Rear and removed from the other end, called the Front
Queues maintain a FIFO ordering property. The queue operations are given below.
- - Queue() creates a new queue that is empty. It needs no parameters and returns an empty queue.
    - - enqueue(item) adds a new item to the rear of the queue. It needs the item and returns nothing.
    - - dequeue() removes the front item from the queue. It needs no parameters and returns the item. The queue is modified.
    - - isEmpty() tests to see whether the queue is empty. It needs no parameters and returns a boolean value.
    - - size() returns the number of items in the queue. It needs no parameters and returns an integer.
'''

class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0,item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)
'''
Deque abstract data type is defined by the following structure and operations. an ordered collection of items where items are added and removed from either end, either front or rear.
- - Deque() creates a new deque that is empty. 
- - addFront(item) adds a new item to the front of the deque. 
- - addRear(item) adds a new item to the rear of the deque.
- - removeFront() removes the front item from the deque. The deque is modified.
- - removeRear() removes the rear item from the deque. The deque is modified.
- - isEmpty() tests to see whether the deque is empty.
- - size() returns the number of items in the deque. returns an integer.
'''
class Deque:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def addFront(self, item):
        self.items.append(item)

    def addRear(self, item):
        self.items.insert(0,item)

    def removeFront(self):
        return self.items.pop()

    def removeRear(self):
        return self.items.pop(0)

    def size(self):
        return len(self.items)
        
'''Queue function'''

def hotPotato(namelist, num):
    simqueue = Queue()
    for name in namelist:
        simqueue.enqueue(name)

    while simqueue.size() > 1:
        for i in range(num):
            simqueue.enqueue(simqueue.dequeue())

        simqueue.dequeue()

    return simqueue.dequeue()

def palchecker(aString):
    chardeque = Deque()

    for ch in aString:
        chardeque.addRear(ch)

    stillEqual = True

    while chardeque.size() > 1 and stillEqual:
        first = chardeque.removeFront()
        last = chardeque.removeRear()
        if first != last:
            stillEqual = False

    return stillEqual
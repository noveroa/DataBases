# unordered, linked list
'''The basic building block for the linked list implementation is the node. Each node object must hold at least two pieces of information. First, the node must contain the list item itself. We will call this the data field of the node. In addition, each node must hold a reference to the next node'''

'''the unordered list will be built from a collection of nodes, each linked to the next by explicit references. As long as we know where to find the first node (containing the first item), each item after that can be found by successively following the next links. With this in mind, the UnorderedList class must maintain a reference to the first node.'''

class Node:
    def __init__(self,initdata):
        self.data = initdata
        self.next = None

    def getData(self):
        return self.data

    def getNext(self):
        return self.next

    def setData(self,newdata):
        self.data = newdata

    def setNext(self,newnext):
        self.next = newnext
        
class UnorderedList:

    def __init__(self):
        self.head = None

    def isEmpty(self):
        return self.head == None

    def add(self,item):
        temp = Node(item)
        temp.setNext(self.head)
        self.head = temp

    def size(self):
        current = self.head
        count = 0
        while current != None:
            count = count + 1
            current = current.getNext()

        return count

    def search(self,item):
        current = self.head
        found = False
        while current != None and not found:
            if current.getData() == item:
                found = True
            else:
                current = current.getNext()

        return found

    def remove(self,item):
        current = self.head
        previous = None
        found = False
        while not found:
            if current.getData() == item:
                found = True
            else:
                previous = current
                current = current.getNext()

        if previous == None:
            self.head = current.getNext()
        else:
            previous.setNext(current.getNext())
    
    def printme(self):
        current = self.head
        alist = []
        while current != None:
            alist.append(current.getData())
            current = current.getNext()

        return alist
    
    def append(self, item):
        
        append = Node(item)
        current = self.head
        
        while current.getNext() != None:
            current = current.getNext()
        
        current.setNext(append)
    
    def index(self,item):
        current = self.head
        previous = None
        found = False
        idx = 0
        while not found:
            
            if current.getData() == item:
                
                found = True
                return idx
            else:
                idx = idx + 1
                previous = current
                current = current.getNext()

        if previous == None:
            self.head = current.getNext()
        else:
            previous.setNext(current.getNext())
        
    def pop(self, index):
        current = self.head
        previous = None
        idx = 0
        while idx != index and current.getNext():
            idx = idx + 1
            previous = current
            current = current.getNext()
        
        if previous == None:
            self.head = current.getNext()

        else :
            previous.setNext(current.getNext())
            
    def insert(self, index, item):
        #use .append to add to the end
        add = Node(item)
        current = self.head
        previous = None
        idx = 0
        while idx != index and current.getNext():
            idx = idx + 1
            previous = current
            current = current.getNext()
        
        if previous == None:
            self.head = add
            add.setNext(current)
        elif not current.getNext():
            print(current.getData())
            previous.setNext(add)
            add.setNext(current)
        else :
            previous.setNext(add)
            add.setNext(current)
            
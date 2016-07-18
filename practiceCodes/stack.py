'''
The Stack Abstract Data Type The stack abstract data type is defined by the following structure and operations. A stack is structured, as described above, as an ordered collection of items where items are added to and removed from the end called the top. Stacks are ordered LIFO. The stack operations are given below.
- - Stack() creates a new stack that is empty. It needs no parameters and returns an empty stack.
- - push(item) adds a new item to the top of the stack. It needs the item and returns nothing.
- - pop() removes the top item from the stack. It needs no parameters and returns the item. The stack is modified.
- - peek() returns the top item from the stack but does not remove it. It needs no parameters. The stack is not modified.
- - isEmpty() tests to see whether the stack is empty. It needs no parameters and returns a boolean value.
- - size() returns the number of items on the stack. It needs no parameters and returns an integer.
'''

class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
         return self.items == []

    def push(self, item):
         self.items.append(item)

    def pop(self):
    #only top can be removed from a stack
         return self.items.pop()

    def peek(self):
         return self.items[len(self.items)-1]

    def size(self):
         return len(self.items)
        
    def contains(self, item):
         return item in items
    
    def reverse_stack(self):
        self.items.reverse()
            
            
        
        
'''Stack related functions'''        
        
def revstring(mystr):
    '''
    : param : mystr : string.  
    : returns : reverse of the given string as a string'''
    s = Stack()
    #c = Stack()
    for a in mystr: 
        s.push(a)
        #c.push(a)

    rev = ''
    while not s.isEmpty():
        rev = rev +  s.pop()
    #while not c.isEmpty():
        #rev2 = ''.join([c.pop() for i in np.arange(0,c.size())])
   
    
    return rev#, rev2

def baseConverter(decNumber,base):
    digits = "0123456789ABCDEF"

    remstack = Stack()

    while decNumber > 0:
        rem = decNumber % base
        remstack.push(rem)
        decNumber = decNumber // base

    newString = ""
    while not remstack.isEmpty():
        newString = newString + digits[remstack.pop()]

    return newString
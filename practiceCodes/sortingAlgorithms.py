'''SORTING ALGORITHMS
- - sequential search is O(n) for ordered and unordered lists.
- - A binary search of an ordered list is O(logn) in the worst case.
- - Hash tables can provide constant time searching.
- - A bubble sort, a selection sort, and an insertion sort are O(n2) algorithms.

- - A merge sort is O(nlogn), but requires additional space for the merging process.
- - A quick sort is O(nlogn), but may degrade to O(n2) if the split points are not near the middle of the list. It does not require additional space.
'''


def binary_search(myOrderedArray, item):
    
    ''' Taking an already ordered list. O(logn) -> halving search each time!
    
    : param myOrderedList ordered python array of comparable items (chars, integers, floats...): 
    : param item python object : 
    : returns boolean True if item found in list, False otherwise
    '''
    first = 0
    last = len(myOrderedArray)-1
    found = False
    i = 0
    while (first <= last) and (not found):
        midpoint = (first + last) // 2 #floor function
        
        if myOrderedArray[midpoint] == item:
            print('found it'), i
            found = True
        
        else:
            i  =+1
            if item < myOrderedArray[midpoint]:
                last = midpoint - 1
            else :
                first = midpoint + 1
    return found, 'Took %d times'%i



def quickSort(alist):
    '''QUICKSORT O(n): memory: inplace
    : param mylist : python list/array
    '''
    
    quickSortHelper(alist,0,len(alist)-1)

def quickSortHelper(alist,first,last):
    if first<last:

        splitpoint = partition(alist,first,last)

        quickSortHelper(alist,first,splitpoint-1)
        quickSortHelper(alist,splitpoint+1,last)

def partition(alist,first,last):
    
    pivotvalue = alist[first]

    leftmark = first+1
    rightmark = last

    done = False
    
    while not done:

        while leftmark <= rightmark and alist[leftmark] <= pivotvalue:
            leftmark = leftmark + 1

        while alist[rightmark] >= pivotvalue and rightmark >= leftmark:
            rightmark = rightmark -1

        if rightmark < leftmark:
            done = True
        else:
            temp = alist[leftmark], alist[rightmark] = alist[rightmark], alist[left]
            

    alist[first], alist[rightmark] = alist[rightmark], alist[first]


    return rightmark

def mergeSort(alist):
    '''  O(nlogn) works on left, then merges to the right
    
    : param mylist python list/array
    '''
    print alist
    if len(alist) > 1:

        midpoint = len(alist)//2
        
        left = alist[:midpoint]
        right = alist[midpoint:]

        mergeSort(left)
        mergeSort(right)
        
        
        i,j,k = 0,0,0
        
        while i < len(left) and j < len(right):
            if left[i] < right[j]:
                alist[k] = left[i]
                i = i + 1
            else:
                alist[k] = right[j]
                j = j + 1
            k = k + 1
        while i < len(left):
            alist[k] = left[i]
            i = i + 1
            k = k + 1
        while j < len(right):
            alist[k] = right[j]
            j = j + 1
            k = k + 1
        print("Merging ",alist)
        
def bubbleSort(mylist):
    '''  O(n^2) 
        A bubble sort is often considered the most inefficient sorting method since it must 
        exchange items before the final locatioN is known. These wasted exchange operations 
        are very costly. However, because the bubble sort makes passes through the entire unsorted 
        portion of the list, it has the capability to do something most sorting algorithms cannot
    
    : param mylist python list/array
    '''
    for passnum in range(len(mylist)-1,0,-1):
        for i in range(passnum):
            if mylist[i]>mylist[i+1]:
                mylist[i], mylist[i+1] = mylist[i+1], mylist[i]


def shortBubbleSort(mylist):
    '''  O(n^2) way to get out of the entire 'wasted exchanges'
    
    : param mylist python list/array
    '''
    exchanges = True
    passnum = len(mylist)-1
    while passnum > 0 and exchanges:
        exchanges = False
        for i in range(passnum):
            if mylist[i]>mylist[i+1]:
                exchanges = True
                mylist[i], mylist[i+1] = mylist[i+1], mylist[i]
                
        passnum = passnum-1
        
def selectionSort(mylist):
    '''  O(n^2) but one exchange per pass and thus runs quicker than Bubble
    
    : param mylist python list/array
    '''
    for fillslot in range(len(mylist)-1,0,-1):
        positionOfMax=0
        for location in range(1,fillslot+1):
            if mylist[location]>mylist[positionOfMax]:
                positionOfMax = location

        mylist[fillslot], mylist[positionOfMax] = mylist[positionOfMax], mylist[fillslot]

def insertionSort(mylist):
    '''  O(n^2) but one exchange and maintains a sorted sublist
    
    : param mylist python list/array
    '''
    for index in range(1,len(mylistt)):
        currentvalue = mylist[index]
        position = index

        while position>0 and mylist[position-1]>currentvalue:
            mylist[position]=mylist[position-1]
            position = position-1

        mylist[position]=currentval
        
def kthSmallest(mylist, k):
    '''Kth Smallest O(nlogn) becuase of sorting
    : param mylist : python list/array
    : param k integer : index value of item to return'''
    
    mylist.sort()
 
    return mylist[k-1]


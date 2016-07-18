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
        

def kthSmallest(mylist, k):
    '''Kth Smallest O(nlogn) becuase of sorting
    : param mylist : python list/array
    : param k integer : index value of item to return'''
    
    mylist.sort()
 
    return mylist[k-1]


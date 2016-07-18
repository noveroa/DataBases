def anagramSolution1(s1,s2): #n^2
    alist = list(s2)

    pos1 = 0
    stillOK = True

    while pos1 < len(s1) and stillOK:
        pos2 = 0
        found = False
        while pos2 < len(alist) and not found:
            if s1[pos1] == alist[pos2]:
                found = True
            else:
                pos2 = pos2 + 1

        if found:
            alist[pos2] = None
        else:
            stillOK = False

        pos1 = pos1 + 1

    return stillOK


def anagramSolutionSort(s1,s2): #STILL n^2 because of sort
    a1 = list(s1)
    a2 = list(s2)
    a1.sort()
    a2.sort()
    pos = 0
    matches = True

    while pos < len(a1) and matches:
        if a1[pos]==a2[pos]:
            pos = pos + 1
        else:
            matches = False

    return matches
def anagramSolutionLinear(s1,s2):  ##NO NESTING!
    c1 = [0]*26
    c2 = [0]*26

    for i in range(len(s1)):
        pos = ord(s1[i])-ord('a')
        #print(s1[i], ord(s1[i]), ord('a'))
        c1[pos] = c1[pos] + 1

    for i in range(len(s2)):
        pos = ord(s2[i])-ord('a')
        c2[pos] = c2[pos] + 1

    j = 0
    stillOK = True
    while j<26 and stillOK:
        if c1[j]==c2[j]:
            j = j + 1
        else:
            stillOK = False

    return stillOK
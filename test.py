import pandas as pf

def all_perms(elements, c= []):
    if len(elements) <=1:
        c.append(elements)
        yield elements
    else:
        for perm in all_perms(elements[1:]):
            for i in range(len(elements)):
                # nb elements[0:1] works in both string and list contexts
                yield perm[:i] + elements[0:1] + perm[i:]

f = [g for g in all_perms(['a','b','c'])]

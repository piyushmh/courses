
def xxx(a):
    a+=1
    yield a;
    a+=1
    yield a;
    a+=1
    yield a;
    
func = xxx(1)
print func.next()
print func.next()
print func.next()
print func.next()

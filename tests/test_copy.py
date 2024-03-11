class Test:
    def __init__(self,a,b):
        self.a = a
        self.lst = b

    def __copy__(self):
        return Test(self.a, list(self.lst))

val = 15
my_lst = [1,2,3,4,5]

var1 = Test(val, my_lst)
var2 = var1.copy()

print(var1 is var2)
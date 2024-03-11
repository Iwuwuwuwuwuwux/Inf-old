import test_mod

class Test:
    def __init__(self):
        self.val = 15

    def baobab(self):
        print(self.val)

val = Test()
test_mod.func(val)
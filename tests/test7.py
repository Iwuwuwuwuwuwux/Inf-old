import tkinter as tk

main = tk.Tk()
main.geometry("500x500")

lst = []

class Test:
    def __init__(self):
        self.frame = None

    def func(self, x, y):
        global lst

        def fnc(): self.frame = tk.Label(main, text = "Awowowowowo")
        lst += [lambda: fnc()]
        lst += [lambda: self.frame.place(x = x, y = y, anchor = "nw")]

tt = Test()
tt.func(100, 100)
tt.func(200, 200)
tt.func(300, 300)
tt.func(400, 400)

while True:
    if not len(lst) == 0:
        for elt in lst:
            elt()

        lst = []

    main.update()
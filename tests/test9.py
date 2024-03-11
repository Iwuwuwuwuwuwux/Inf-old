import tkinter as tk

main = tk.Tk()
main.geometry("500x500")

frame = tk.Frame(main, width = 300, height = 300, bg = "purple")
frame.place(x = 250, y = 250, anchor = "center")

def callback1(e):
    print("callback1")

def callback2(e):
    print("callback2")

frame.bind("<Button-1>", callback1)
frame.bind("<Button-1>", callback2)

frame2 = tk.Frame(main, width = 50, height = 50, bg = "red")
frame2.place(x = 250, y = 250, anchor = "center")
frame2.bind("<Button-1>", callback1)
frame.bind("<Motion>", lambda e: print(e.x, e.y))


main.bind("<KeyPress-a>", lambda e: print("key \"a\" pressed", e.x, e.y))

main.mainloop()
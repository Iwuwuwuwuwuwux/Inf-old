import tkinter as tk
import threading
from time import sleep

main = tk.Tk()
main.geometry("800x800")

canvas = tk.Canvas(main, width = 400, height = 400, bg = "purple")
canvas.place(x=400, y=400, anchor="center")

def cb_click_canvas(e):
    print(e.x, " - ", e.y)

canvas.bind("<Button-1>", cb_click_canvas)

def delayed_func():
    global canvas

    sleep(3)

    canvas.destroy()

threading.Thread(target=delayed_func).start()

main.mainloop()
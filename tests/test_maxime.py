#Import tkinter library
from tkinter import *
import threading
from PIL import Image, ImageTk
#Create an instance of tkinter frame or window

lst = []

def thread_func():
    global lst

    while True:
        if len(input("cmd:")) == 0:
            print(lst)

thrd = threading.Thread(target = thread_func)
thrd.start()


win= Tk()
#Set the geometry of tkinter frame
win.geometry("1000x500")

background = Image.open("tests/test_samples/resized_image.png").resize((1000, 500))
tk_image = ImageTk.PhotoImage(image=background)
background_wdgt = Label(win, image = tk_image)
background_wdgt.place(x=0, y=0)
background_wdgt.image = tk_image

def callback(e):
   global lst

   x= e.x
   y= e.y

   lst += [(x, y)]

win.bind('<Button 1>',callback)
win.mainloop()
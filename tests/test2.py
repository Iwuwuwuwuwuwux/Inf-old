# Import the required libraries
from tkinter import *
from PIL import Image, ImageTk, ImageOps
from time import sleep
from math import cos, radians
import threading

# Create an instance of tkinter frame or window
win=Tk()
# Set the size of the tkinter window
win.geometry("700x350")
# Load the image
image=Image.open('tests/test_samples/resized_image.png')

# Conver the image in TkImage
def resize():
    global label, i, v
    """
    if not v: return
    n_image_object = image.resize((abs(i) + 1, 350))

    val = i
    if val < 0:
        n_image_object = ImageOps.mirror(n_image_object)

    n_img=ImageTk.PhotoImage(image=n_image_object)

    label.configure(image = n_img)
    label.image = n_img"""
    
# Display the image with label
label=Label(win, image=ImageTk.PhotoImage(image))
label.pack()

i = 450
ang = 0
v = True
w = False

def func():
    global label, v, w

    sleep(5)

    while w: sleep(0.05)
    w = True
    v = False
    w = False
threading.Thread(target = func).start()

while True:
    win.update()

    while w: sleep(0.05)
    w = True
    resize()
    w = False
    
    if not v: label.destroy()

    ang = (ang + 0.4) % 360
    i = int(450 * cos(radians(ang)))


    
import tkinter as tk
from PIL import Image, ImageTk

main = tk.Tk()
main.geometry("500x500")

canvas = tk.Canvas(main, width = 500, height = 500)
canvas.place(x=0, y=0)

img = Image.open("tests/test_samples/resized_image.png").resize((500, 500))
img_tk = ImageTk.PhotoImage(image = img)

label = tk.Label(canvas, image = img_tk)
label.place(x = 0, y = 0, anchor = "nw")

main.mainloop()

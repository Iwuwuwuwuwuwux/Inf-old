import modules.sprite as sprite
import modules.game as game

from tkinter import *
from PIL import Image, ImageTk
import threading
from time import sleep

main = Tk()
main.geometry("500x500")
main.update()

model = {
    "images": {
        "homme1": Image.open("tests/test_samples/homme1.png"),
        "homme2": Image.open("tests/test_samples/homme2.png"),
        "homme3": Image.open("tests/test_samples/homme3.png")
    },
    "sequences": {
        "swap": [True, "homme1", 2000, "homme2", 2000, "homme3", 2000]
    }
}
game = game.Game()

new_sprite = sprite.Sprite(game, main, model, "homme1", (250,250), (100,100))
new_sprite.start_sequence("swap")
new_sprite.sequence_time_factor = 2

def thread_func():
    sleep(5)
    new_sprite.stop_sequence()

threading.Thread(target=thread_func, name="stop_swap").start()

while True:
    main.update()

    if not len(sprite.funcs_exec_queue) == 0:
        for elt in sprite.funcs_exec_queue[game.tkinter_thread_id]:
            elt()

    print("b")

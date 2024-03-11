import threading

targets = []
exchange = []

def func():
    global targets

    a = 8
    b = 9

    targets += [lambda: a+b]

def thread_func():
    global exchange

    for elt in targets:
        exchange += [elt()]

    while True: 1+1

threading.Thread(target=thread_func).start()
func()
while True:
    if len(exchange) != 0:
        for elt in exchange:
            print(elt)
        
        exchange = []
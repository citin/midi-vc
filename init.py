import mido

# inport = mido.open_input('OpenInput', virtual=True)
outport = mido.open_output('AndresVirtualInstrument', virtual=True)

from mido import Message
msg1 = Message('note_on', note=60)
msg2 = Message('note_on', note=62)

from pynput import mouse
from time import sleep

from threading import Thread

def stop_note_async(x, y):
    sleep(1)
    outport.send(Message('note_off', note=int(x), velocity=int(y)))

def on_move(x, y):
    if (1 <= int(x) <= 127) & (1 <= int(y) <= 127):
        outport.send(Message('note_on', note=int(x), velocity=int(y)))
        subproceso = Thread(target=stop_note_async, args=(x, y))
        subproceso.start()
        
# Collect events until released
with mouse.Listener(
        on_move=on_move,
        ) as listener:
    listener.join()

import time
from machine import Pin, freq
from ir_rx.print_error import print_error
from ir_rx.acquire import IR_GET
from ir_tx import Player
from pimoroni import Button
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY, PEN_P4
import json


display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, pen_type=PEN_P4, rotate=180)
display.set_backlight(0.5)
display.set_font("bitmap8")

button_a = Button(12)
button_b = Button(13)
button_x = Button(14)
button_y = Button(15)

BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)

pin_power_ir_r = Pin(27, Pin.OUT, value=1)

# (pin, freq, asize, duty, verbose)
ir_t = Player(Pin(5, Pin.OUT, value=0))
WIDTH, HEIGHT = display.get_bounds()
have_sig = False
freqs = []

f = open("ir_storage.txt", "a+")
try:
    f.seek(0)
    merp = f.readlines()
    for m in merp:
        freqs.append(json.loads(m))
    current_count = len(freqs)
    if current_count:
        have_sig=True
    else:
        current_count = 1
except Exception as e:
    freqs = []
    current_count = 1

def clear_screen():
    display.set_pen(BLACK)
    display.clear()
    display.update()
    
def main_screen():
    clear_screen()
    display.set_pen(WHITE)
    display.text("Please choose option:", 0, 0, 240, 3)
    display.text("Button Y - Record IR", 0, int(HEIGHT*2/4), 240, 2)
    display.text("Button X - Replay IR", 0, int(HEIGHT*3/4), 240, 2)
    display.update()

def choice_screen(c):
    clear_screen()
    display.set_pen(WHITE)
    display.text("Signal"+str(c), 0, int(HEIGHT*2/4), 240, 2)
    display.update()

def record_signal_screen():
    clear_screen()
    display.set_pen(WHITE)
    display.text("Waiting for signal...", 10, 10, 240, 2)
    display.update()
    # (pin, nedges, tblock, callback, *args)
    ir_r = IR_GET(Pin(26, Pin.IN), 100, 100)
    data = ir_r.acquire()
    freqs.append({current_count:data})
    f.write(json.dumps({current_count:data}))
    display.text("Signal acquired", 10, int(HEIGHT*2/4), 240, 2)
    display.update()
    current_count += 1
    time.sleep(2)
    return data

clear_screen()
main_screen()

while True:
    if button_y.read():
        record_signal_screen()
        have_sig = True
        main_screen()
    if button_x.read():
        if have_sig:
            make_choice = False
            count = 1
            while not make_choice:
                if button_b.read():
                    count += 1
                    choice_screen(count)
                if button_a.read():
                    if count > 0:
                        count -= 1
                        choice_screen(count)
                if button_x.read():
                    clear_screen()
                    display.set_pen(WHITE)
                    display.text("Replaying signal: " + str(count), 0, int(HEIGHT/2), 240, 2)
                    display.update()
                    d = freqs[count]
                    ir_t.play(d)
                    time.sleep(1)
                    make_choice = True
        else:
            clear_screen()
            display.set_pen(WHITE)
            display.text("You have not captured a signal yet", 10, 10, 240, 2)
            display.update()
            time.sleep(1)
        main_screen()
    
    
import board
import time
import rotaryio
from digitalio import DigitalInOut, Direction, Pull


UNITS = 4 # number of knobs / switches
VOLUME_STEP = 32 # step to inc/dec volume, max is 1023
STARTING_VOLUME = 512 # initial volume to be set at startup

class Knob:
    def __init__(self, clk, dt, sw):
        self.encoder = rotaryio.IncrementalEncoder(dt, clk, 2)
        self.last_position = 0
        self.btn = DigitalInOut(sw)
        self.btn.direction = Direction.INPUT
        self.btn.pull = Pull.UP
        self.value = STARTING_VOLUME

class Switch:
    def __init__(self, btn):
        self.btn = DigitalInOut(btn)
        self.btn.direction = Direction.INPUT
        self.btn.pull = Pull.UP
        self.previousValue = None

def build_serial_message(knobs, switches):
    msg = ''
    for idx, knob in enumerate(knobs):
        if switches[idx].btn.value:
            msg += str(0)
        else:
            if knob.value == 1024: msg += str(1023)
            else: msg += str(knob.value)
        if idx != UNITS - 1:
            msg += "|"
    return msg


# rotary encoder setup here, CLK, DT, SW
# CLK and DT represent rotation directions
# SW is the encoder button / click
knobs = [
    Knob(board.GP0, board.GP1, board.GP2),
    Knob(board.GP3, board.GP4, board.GP5),
    Knob(board.GP6, board.GP7, board.GP8),
    Knob(board.GP9, board.GP10, board.GP11),
]

# the mute switches, intended to match the number of rotary encoders
switches = [
    Switch(board.GP12),
    Switch(board.GP13),
    Switch(board.GP14),
    Switch(board.GP15)
]

last_print_message = '0|0|0|0'

while True:

    for idx, knob in enumerate(knobs):
        if knob.last_position is None or knob.encoder.position != knob.last_position:

            if knob.encoder.position > knob.last_position and knob.value < 1024 and not switches[idx].btn.value:
                knob.value += VOLUME_STEP
            elif knob.encoder.position < knob.last_position and knob.value > 0 and not switches[idx].btn.value:
                knob.value -= VOLUME_STEP

        knob.last_position = knob.encoder.position

        switches[idx].previousValue = switches[idx].btn.value

    message = build_serial_message(knobs, switches)

    if last_print_message != message:
        print(message)
        last_print_message = message

    time.sleep(0.05)  # sleep for debounce


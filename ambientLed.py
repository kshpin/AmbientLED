import sys
import socket
from time import sleep
from colorsys import hsv_to_rgb
import math

# config
DEBUG = False
NUM_LEDS = 180
DEFAULT_MODE = "set"
DEFAULT_CYCLE_RATE = 0.001
DEFAULT_TAIL_LENGTH = 0.8
DEFAULT_RED = 255
DEFAULT_GREEN = 255
DEFAULT_BLUE = 255
DEFAULT_UDP_IP = "192.168.45.105"
DEFAULT_UDP_PORT = 4210

# universal constants
BYTE_MAX = 255
SLEEP_PERIOD = 1/60 # for 60fps


def waves(rate):
    redPeriod = 50
    greenPeriod = 30
    bluePeriod = 37.5

    redSpeed = 0.004
    greenSpeed = 0.010
    blueSpeed = 0.012

    redShift = 0
    greenShift = 0
    blueShift = 0

    t = 0
    while True:
        tuples = []
        for i in range(NUM_LEDS):
            tuples.append((
                (math.sin((t+i)/redPeriod - redShift)+1)/2,
                (math.sin((t+i)/greenPeriod - greenShift)+1)/2,
                (math.sin((t+i)/bluePeriod - blueShift)+1)/2
            ))

        send([round(BYTE_MAX*c) for tp in tuples for c in tp])

        t += rate
        redShift += redSpeed
        greenShift += greenSpeed
        blueShift += blueSpeed
        sleep(SLEEP_PERIOD)

def cycleChristmas(rate):
    t = 0
    while True:
        tuples = []
        for i in range(NUM_LEDS):
            i += math.floor(t*600)

            if (i//100) % 3 == 0:
                tuples.append((0, 255, 0)) # green
            elif (i//100) % 3 == 1:
                tuples.append((255, 0, 0)) # red
            else:
                tuples.append((255, 255, 255)) # yellow

        send([c for tp in tuples for c in tp])

        t += rate
        sleep(SLEEP_PERIOD)

def cycleHeartbeat(rate):
    raise NotImplementedError()

    t = 0
    while True:
        send([])

        t += rate
        sleep(SLEEP_PERIOD)

def cycleSnake(rate, tailLength, r, g, b):
    t = 0
    while True:
        tuples = []
        for x in range(NUM_LEDS):
            a = (x/NUM_LEDS - t)%1 - 1 + tailLength
            a = 0 if a < 0 else a

            tuples.append((a*r, a*g, a*b))

        send([round(c) for tp in tuples for c in tp])

        t += rate*2
        sleep(SLEEP_PERIOD)

def cycleRainbow(type, rate):
    t = 0
    while True:
        tuples = []
        if type == "continuous":
            tuples = [hsv_to_rgb(x/NUM_LEDS + t, 1, 1) for x in range(NUM_LEDS)]
        elif type == "monotonous":
            tuples = [hsv_to_rgb(t, 1, 1)] * NUM_LEDS

        send([round(BYTE_MAX*c) for tp in tuples for c in tp])

        t += rate
        sleep(SLEEP_PERIOD)

def set(r, g, b):
    send([r, g, b] * NUM_LEDS)

def clear():
    set(0, 0, 0)

def send(listData):
    if DEBUG:
        print(len(listData))
        print(listData)

    sock.sendto(bytes(listData), (parsedArgs["--ip"], parsedArgs["--port"]))

def parseArguments(args):
    possibleArguments = { # TODO add --help
        "--ip": "str",
        "--port": "int",
        "--mode": "str",
        "--cycle-rate": "float",
        "--tail-length": "float",
        "--r": "int",
        "--g": "int",
        "--b": "int"
    }

    parsed = {
        "--ip": DEFAULT_UDP_IP,
        "--port": DEFAULT_UDP_PORT,
        "--mode": DEFAULT_MODE,
        "--cycle-rate": DEFAULT_CYCLE_RATE,
        "--tail-length": DEFAULT_TAIL_LENGTH,
        "--r": DEFAULT_RED,
        "--g": DEFAULT_GREEN,
        "--b": DEFAULT_BLUE
    }

    for i in range(0, len(args), 2):
        arg = args[i]
        if arg not in possibleArguments:
            raise ValueError(arg)

        if possibleArguments[arg] == "int":
            parsed[arg] = int(args[i+1])
        elif possibleArguments[arg] == "str":
            parsed[arg] = args[i+1]

    return parsed


parsedArgs = parseArguments(sys.argv[1:])
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

mode = parsedArgs["--mode"]

if mode == "clear":
    clear()
if mode == "set":
    set(parsedArgs["--r"], parsedArgs["--g"], parsedArgs["--b"])
if mode == "christmas":
    cycleChristmas(parsedArgs["--cycle-rate"])
if mode == "waves":
    waves(parsedArgs["--cycle-rate"])
if mode == "continuous_rainbow":
    cycleRainbow("continuous", parsedArgs["--cycle-rate"])
if mode == "monotonous_rainbow":
    cycleRainbow("monotonous", parsedArgs["--cycle-rate"])
if mode == "snake":
    cycleSnake(parsedArgs["--cycle-rate"], parsedArgs["--tail-length"], parsedArgs["--r"], parsedArgs["--g"], parsedArgs["--b"])
if mode == "heartbeat":
    cycleHeartbeat(parsedArgs["--cycle-rate"])

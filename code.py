import board
import pwmio
from adafruit_motor import servo
import time
import neopixel
from digitalio import DigitalInOut, Direction
import adafruit_hcsr04

# enable external power for pixels
external_power = DigitalInOut(board.EXTERNAL_POWER)
external_power.direction = Direction.OUTPUT
external_power.value = True
pwm = pwmio.PWMOut(board.EXTERNAL_SERVO, duty_cycle=2 ** 15, frequency=50)
servo_ext = servo.Servo(pwm)
sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.A2, echo_pin=board.A3)
DISTANCE_THRESHOLD = 60

# variables
NUM_PIXELS = 150
NUM_ACTIVE = 150
pixels = neopixel.NeoPixel(board.EXTERNAL_NEOPIXELS, NUM_PIXELS, bpp=4, brightness=1.0, auto_write=False, pixel_order=neopixel.RGBW)
pixels.fill((0, 0, 0, 0))
pixels.show()

CLOSED_ANGLE = 130
OPEN_ANGLE = 30

# speeds (to whoever is editing this, this is in seconds per step not speed units)
OPENING_SPEED = 0.02
CLOSING_SPEED = 0.02

GOLDEN_ORANGE = (80, 255, 0, 0)
OFF = (0, 0, 0, 0)


def set_pixels(color):
    pixels.fill((0, 0, 0, 0))
    for i in range(NUM_ACTIVE):
        pixels[i] = color
    pixels.show()


def measure_distance():
    try:
        return round(sonar.distance, 1)
    except RuntimeError:
        return 999


def open_box_lid_with_fade(speed=OPENING_SPEED):
    print("opening")
    if CLOSED_ANGLE > OPEN_ANGLE:
        step = -1
    else:
        step = 1
    for angle in range(CLOSED_ANGLE, OPEN_ANGLE + step, step):
        servo_ext.angle = angle
        progress = abs((angle - CLOSED_ANGLE) / max(1, (OPEN_ANGLE - CLOSED_ANGLE)))
        r, g, b, w = GOLDEN_ORANGE
        set_pixels((int(r * progress), int(g * progress), int(b * progress), int(w * progress)))
        time.sleep(speed)
    set_pixels(GOLDEN_ORANGE)
    print("opened")


def close_box_lid_with_fade(speed=CLOSING_SPEED):
    print("closing")
    if CLOSED_ANGLE > OPEN_ANGLE:
        step = 1
    else:
        step = -1
    for angle in range(OPEN_ANGLE, CLOSED_ANGLE + step, step):
        servo_ext.angle = angle
        progress = 1.0 - abs((angle - OPEN_ANGLE) / max(1, (CLOSED_ANGLE - OPEN_ANGLE)))
        r, g, b, w = GOLDEN_ORANGE
        set_pixels((int(r * progress), int(g * progress), int(b * progress), int(w * progress)))
        time.sleep(speed)
    set_pixels(OFF)
    print("closed")


servo_ext.angle = CLOSED_ANGLE
set_pixels(OFF)

box_is_open = False

while True:
    d = measure_distance()
    print(f"dist {d} cm")
    if d <= DISTANCE_THRESHOLD and not box_is_open:
        open_box_lid_with_fade()
        box_is_open = True
    elif d > DISTANCE_THRESHOLD and box_is_open:
        close_box_lid_with_fade()
        box_is_open = False
    time.sleep(0.1)

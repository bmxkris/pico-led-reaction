import board
import neopixel
import digitalio
import random
import time
from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.group import AnimationGroup
from adafruit_led_animation.color import RED, GREEN, WHITE, PURPLE, AMBER
from adafruit_debouncer import Debouncer
import fourdigitsevensegmentLEDdisplay as led_display

num_pixels = 50
brightness = 1
game_counter = {
    '1': 0,
    '2': 0
}


def create_button(gpio_pin):
    pin = digitalio.DigitalInOut(gpio_pin)
    pin.direction = digitalio.Direction.INPUT
    pin.pull = digitalio.Pull.DOWN
    return Debouncer(pin)

def init_game(pixels, pixels2, button1, button2, reset_button):

    game_started = False
    game_winner = 0
    start_time = time.monotonic()
    delay_time = random.random() * 5

    while not game_winner:
        button1.update()
        button2.update()

        if game_started is False:
            pixels.fill(RED)
            pixels2.fill(RED)
            pixels.show()
            pixels2.show()

        if time.monotonic() > (start_time + delay_time) and game_started is False:
            game_started = True
            game_start_time = time.monotonic()
            pixels.fill(GREEN)
            pixels2.fill(GREEN)
            pixels.show()
            pixels2.show()

        if button1.fell:
            if game_started is False:
                #  if you pressed the button too soon, reset the start time
                game_start_time = time.monotonic()

            if game_started is True:
                game_winner = 1
                winner_animation(pixels, pixels2, game_winner, game_start_time)

        if button2.fell:
            if game_started is False:
                #  if you pressed the button too soon, reset the start time
                game_start_time = time.monotonic()

            if game_started is True:
                game_winner = 2
                winner_animation(pixels2, pixels, game_winner, game_start_time)

    return True

def winner_animation(pixels, pixels2, game_winner, game_start_time):

    reaction_time = time.monotonic() - game_start_time
    #  print (reaction_time)
    if game_winner == 1:
        game_counter['1'] += 1
    else:
        game_counter['2'] += 1

    animations = AnimationGroup(
        Blink(pixels, speed=0.07, color=WHITE),
        Pulse(pixels2, speed=0.01, color=PURPLE),
    )

    animation_start_time = time.monotonic()

    while time.monotonic() < animation_start_time + 5:
        animations.animate()
        if time.monotonic() < animation_start_time + 2.5:
            led_display.display_number(reaction_time)
        else:
            led_display.display_number(str(game_counter['1']) + '--' + str(game_counter['2']))

    if game_counter['1'] == 9 or game_counter['2'] == 9:
        game_counter['1'] = 0
        game_counter['2'] = 0


def standby_animation(pixels, pixels2, button1, button2, reset_button):
    sparkle = AnimationGroup(
        Sparkle(pixels, speed=0.1, color=AMBER, num_sparkles=10),
        Sparkle(pixels2, speed=0.1, color=AMBER, num_sparkles=10),
    )

    while True:
        reset_button.update()
        # standby animation
        sparkle.animate()

        if reset_button.fell:
            init_game(pixels, pixels2, button1, button2, reset_button)

def setup_and_standby():
    pixels = neopixel.NeoPixel(board.GP2, num_pixels, brightness=brightness, auto_write=False)
    pixels2 = neopixel.NeoPixel(board.GP3, num_pixels, brightness=brightness, auto_write=False)

    reset_button = create_button(board.GP28)
    button1      = create_button(board.GP26)
    button2      = create_button(board.GP27)

    standby_animation(pixels, pixels2, button1, button2, reset_button)

if __name__ == '__main__':  # Program starting from here

    setup_and_standby()


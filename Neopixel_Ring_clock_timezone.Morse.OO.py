"""
Object-oriented version of ring clock with pytz timezone awareness.
4 February 2026
Added power-on Morse message 10 February 2026
Added top of hour Morse message 11 February 2026
DK
"""
#! /usr/bin/python3

from datetime import datetime
import time
import pytz
# deprecated.  Should use Use datetime.timezone.utc instead of pytz.UTC.
# Use the datetime constructor parameter tzinfo or .replace() instead of .localize().
# Remove .normalize() calls. If the datetime is timezone-aware, then the wall time arithmetic should work even across daylight saving time clock changes. More on that in the Gotcha section below!
# Use zoneinfo.ZoneInfo instead of pytz.timezone to get a tzinfo object.
import board
import neopixel
import sys


class NeoPixelClock:
    # enough Morse for W8EDU, N8OBJ, W8EDU, and attention signal "V".  Add as necessary.
    MORSE = {
        'A': '.-',
        'B': '-...',
        'D': '-..',
        'E': '.',
        'J': '.---',
        'N': '_.',
        'O': '___',
        'U': '..-',
        'Y': '-.--',
        'V': '...-',
        'W': '.--',
        '8': '---..',
        'SK': '...-.-',
        ' ': ' ',
    }
    
    def __init__(
        self,
        pixel_pin=board.D18,
        num_pixels=60,
        timezone="US/Eastern",
        intensity=25,
        brightness=0.2,
    ):
        # Time
        self.tz = pytz.timezone(timezone)

        # LED geometry
        self.num_pixels = num_pixels
        self.leds_per_hour = num_pixels // 12
        self.minutes_per_led = 60 // self.leds_per_hour

        # Brightness
        self.intensity = intensity

        # Colors (intentionally tuned, not literal RGB names)
        self.RED     = (0, intensity, 0)
        self.GREEN   = (intensity // 2, 0, 0) # green is dimmed to correspond to visual perception
        self.BLUE    = (0, 0, intensity)
        self.WHITE   = (intensity, intensity, intensity)
        self.YELLOW  = (intensity, intensity, 0)
        self.CYAN    = (0, intensity, intensity)
        self.MAGENTA = (intensity, 0, intensity)
        self.OFF     = (0, 0, 0)

        # NeoPixel setup
        self.pixels = neopixel.NeoPixel(
            pixel_pin,
            num_pixels,
            brightness=brightness,
            auto_write=False,
            pixel_order=neopixel.RGB,
        )

        self.clear() # shut off entire NeoPixel string; equivalent to np.fill((0,0,0))

    # ---------- Hardware helpers ----------

    def clear(self):
        self.pixels.fill(self.OFF)
        self.pixels.show()

    # ---------- Time math ----------
    # generalized this in case 24 pixel ring ever used

    def hour_led(self, hour, minute):
        return (
            (hour % 12) * self.leds_per_hour
            + (minute // self.minutes_per_led)
        )

    # ---------- Drawing ----------

    def draw(self, sec, minute, hour):
        self.pixels.fill(self.OFF)
        hour_led = self.hour_led(hour, minute)

        if sec == minute == hour_led: # i.e., all the clock hands are together
            self.pixels[sec] = self.WHITE

        elif sec == minute:           # second and minute hands together...etc.
            self.pixels[sec] = self.YELLOW
            self.pixels[hour_led] = self.BLUE

        elif sec == hour_led:
            self.pixels[sec] = self.CYAN
            self.pixels[minute] = self.GREEN

        elif minute == hour_led:
            self.pixels[minute] = self.MAGENTA
            self.pixels[sec] = self.RED

        else:                         # all three clock hands on different LEDs
            self.pixels[sec] = self.RED
            self.pixels[minute] = self.GREEN
            self.pixels[hour_led] = self.BLUE

        self.pixels.show()
        
    # ---------- Flash top LED in Morse ----------
    def flash_morse(self, message, led=0, time_unit=0.18, last_string=True):
        DOT = time_unit
        DASH = 3 * time_unit
        INTRA = time_unit
        INTER = 3 * time_unit
        INTERWORD= 7 * time_unit

        for char in message:
            pattern = self.MORSE.get(char.upper())
            if not pattern: # if the pattern is empty
                continue

            for symbol in pattern:
                self.pixels[led] = self.WHITE
                self.pixels.show()

                time.sleep(DOT if symbol == '.' else DASH)

                self.pixels[led] = self.OFF
                self.pixels.show()
                time.sleep(INTRA)

            time.sleep(INTER) # end each symbol with intersymbol time
            
        time.sleep(INTERWORD) # end each string with interword time


    # ---------- Main loop ----------

    def run(self):
        def flash_ID():
            self.flash_morse("VVV", led=0, time_unit=0.1)
            self.flash_morse("W8EDU", led=0, time_unit=0.1)
            self.flash_morse("VVV", led=0, time_unit=0.1)

        flash_ID() # at powerup
        
        now = datetime.now(self.tz)
        sec = now.second

        # Use console for onscreen reference. Alignment:
        print("\n")
        for _ in range(sec):
            print(" ", end="")
            sys.stdout.flush()

        try:
            while True:
                now = datetime.now(self.tz)
                sec = now.second
                minute = now.minute
                hour = now.hour
                
                # run the console
                print("*", end="")
                sys.stdout.flush()

                # run the ring of LEDs
                self.draw(sec, minute, hour)

                # wait for next second
                while datetime.now(self.tz).second == sec:
                    time.sleep(0.005) # use this instead of pass to keep microprocessor cool

                if (minute == sec == 0):
                    print('\ntop of hour')
                    flash_ID() # works but stops the clock hands
                    # need to keep console going.
                    # ? run separate process so clock can continue, too?

                if sec == 0: # new minute starting, show that on console
                    print("\n")
                    if minute == 0:
                        print("hour ", hour, "\n")
                    print("hour: ", hour, "  minute: ", minute)

        except KeyboardInterrupt: # keypress in console clears the LEDs and shuts off the clock
            self.clear()


# ---------- Entry point ----------

if __name__ == "__main__":
    clock = NeoPixelClock()
    clock.run()

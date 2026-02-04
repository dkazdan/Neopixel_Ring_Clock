"""
Object-oriented version of ring clock with pytz timezone awareness.
4 February 2026
DK
"""
#! /usr/bin/python3

from datetime import datetime
import time
import pytz
"""deprecated.  Should use Use datetime.timezone.utc instead of pytz.UTC.
Use the datetime constructor parameter tzinfo or .replace() instead of .localize().
Remove .normalize() calls. If the datetime is timezone-aware, then the wall time arithmetic should work even across daylight saving time clock changes. More on that in the Gotcha section below!
Use zoneinfo.ZoneInfo instead of pytz.timezone to get a tzinfo object."""
import board
import neopixel
import sys


class NeoPixelClock:
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

    # ---------- Main loop ----------

    def run(self):
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

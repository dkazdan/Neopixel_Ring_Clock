#! /usr/bin/python3

"""
Python code to run clock on ring of 60 NeoPixels.
Neopixel code must run in root.
? Sound needs to be off for GPIO18 ?
Started 12 September 2023
8 November 2023:
    Works pretty well.
    TODO: Add yellow background for sunup time, blue for moon up
29 December 2023:
    Corrected error in all-on hour computation
Clockpi5 built 12 February 2024
Needs Adafruit-blinka and Adafruit-neopixel.
Runs on Pi's time zone for now.
DK
20 July 2025 Verified that it's all still working.
"""


from datetime import datetime
import time
import pytz      # https://pypi.org/project/pytz/
import board     # import the adafruit libraries
import neopixel  # this may be a Raspberry Pi library only.
import sys


# NeoPixels must be connected to D10, D12, D18 or D21 to work.
# Usual is D18. ? Need audio off ? Did that on Piclock5
pixel_pin = board.D18
tz = pytz.timezone('US/Eastern')

# trial and error LED brightness.  Max of 255 is very bright unfiltered.
# This interacts with the brightness variable in neopixel.Neopixel.
intensity = 25

# The number of NeoPixels in the clock ring
# 60 seconds per minute red, 60 minutes per hour green, 60 fifths of an hour blue per twelve hours
num_pixels = 60

# The order of the pixel colors - RGB or GRB.
ORDER = neopixel.RGB

# Declare array of neopixels
pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
    )

# turn off all the pixels to start
fill_off=(0,0,0)
pixels.fill(fill_off)
pixels.show()

# print statements are console diagnostics, don't affect clock LEDs
print('\r\n')


now = datetime.now(tz)
secnow=now.second # need initial seconds to begin console printing clock
minnow=now.minute
hournow=now.hour

# start the console clock here
for i in range(secnow): # print blanks to make up the beginning of the console clock
    print(' ', end="")
    sys.stdout.flush() # needed to print to console; not needed in Thonny.

# continue with both console and LED ring clock here
try:
    while(True):               # main loop for both LEDs and console
        pixels.fill(fill_off)  # shut off all the pixels--or shut off previous, light new
        print('*', end="")  # always print the second tick
        sys.stdout.flush()
        
        hourLED=(hournow%12)*5 + (minnow//12)   # Advance blue 5 pixels every hour in 12 hour time, not 24 hour
        
        # check on hand crossings and color mixing to show overlaps correctly
    #    if (secnow==minnow and secnow==hournow): # seconds, minutes, hour all coincide  # error here?
        if (secnow==minnow==hourLED):               # seconds, minutes, hour LED all coincide
            all_on=(intensity,intensity,intensity)
            pixels[secnow]=all_on
        elif (secnow==minnow):
            pixels[secnow]=(intensity,intensity,00)        # seconds and minutes coincide
            pixels[hourLED]=(00,      00,       intensity)
        elif (secnow==hourLED):
            pixels[secnow]=(00,       intensity,intensity) # seconds and hour coincide
            pixels[minnow]=(intensity,00,       00)
        elif (minnow==hourLED):
            pixels[minnow]=(intensity,00,       intensity) # minutes and hour coincide
            pixels[secnow]=(00,       intensity,00)
        else:                                              # if got here, they're all different.
            pixels[secnow]=(00,       intensity,00)        # red for seconds
            pixels[minnow]=(intensity,00,       00)        # green for minute
            pixels[hourLED]=(00,      00,       intensity) # blue for hour
        
        pixels.show()
        
        while(secnow==datetime.now(tz).second):
            time.sleep(0.005)   # 5 ms is plenty; use this instead of pass to keep processor cool
        now = datetime.now(tz)  # update second
        secnow  = now.second  # need to update secnow for the while loop
        minnow  = now.minute
        hournow = now.hour

        if secnow==0:  # console: start new line at each top of minute
            print('\r\n')
            if (now.minute==0):
                print("hour ", now.hour, '\r\n')
            print("hour: ", now.hour, "  minute: ", now.minute)

except KeyboardInterrupt:
    pixels.fill((0,0,0))
    pixels.show()
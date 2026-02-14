Python code to run a clock, using a 60 LED Neopixel ring.
The code takes a timezone using pytz; this should be updated.
It has hardcoded a Morse message to be flashed on the zero-position LED
at startup and at the top of each hour.  The library of Morse is not complete;
check if all the characters are available for any new ID used and add
to the library as necessary.

Changes might be to remove the background clock illumination from
the zero LED during Morse transmission.

The Python code used now to continue the clock during the Morse is
slightly jerky.  Moving that out to a separate process or thread
would improve it but would add code complexity.

The entire task might be done for about $10 less with a Pi Pico W.

Using a GPS receiver instead of WiFi is also a possibility.  Timezone
could be set by GPS position in that case.

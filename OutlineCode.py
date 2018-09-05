# EEE3096S_EnvironmentMonitor
#!/usr/bin/python
import RPi.GPIO as GPIO
import spidev
import os
import sys
import time

spi = spidev.SpiDev()
spi.open(0,0)
GPIO.setmode(GPIO.BCM)

reset = 21
frequency = 4
stopbtn = 17
display = 27


GPIO.setup(reset, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(frequency, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(stopbtn, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(display, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
channel = 0
delay = 0.5

def re(channel1):													   	   #functions that are called
    print("re")                                                            #when the event/interrupt occurs

def freq(channel):
    print("freq")

def stop(channel):
    print("stop")

def disp(channel):
    print("disp")

def GetData(channel):											           #ADC data collection function
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]
    return data

def ConvertVolts(data, places):
    volts = (data*3.3)/float(1023)
    volts = round(volts,places)
    return volts

try:                                                                       #try/except conditional for ADC data collection.
    while True:                                                            #Event additions can go above this i think
        sensor_data = GetData(channel)
        sensor_volt = ConvertVolts(sensor_data,2)
        time.sleep(delay)

except KeyboardInterrupt:
    spi.close()

print(sensor_volt)                                                          #testing ADC/ADC code
GPIO.add_event_detect(reset, GPIO.RISING, callback=re, bouncetime=200)		#Event detector initialization

GPIO.add_event_detect(frequency, GPIO.RISING, callback=freq, bouncetime=200)

GPIO.add_event_detect(stopbtn, GPIO.RISING, callback=stop, bouncetime=200)

GPIO.add_event_detect(display, GPIO.RISING, callback=disp, bouncetime=200)

try:
    GPIO.wait_for_edge(reset, GPIO.FALLING)                                 #I think this try/except condition can go

except KeyboardInterrupt:
    GPIO.cleanup()

GPIO.cleanup()

# EEE3096S_EnvironmentMonitor
#!/usr/bin/python
import RPi.GPIO as GPIO
import spidev
import os
import time

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1000000

GPIO.setmode(GPIO.BCM)

reset = 21
frequency = 4
stopbtn = 17
display = 27

GPIO.setup(reset, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(frequency, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(stopbtn, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(display, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

potChan = 0
tempChan = 1
ldrChan = 2

delay = 0.5
monitor = False
Reset = False
carry = False
cdata = []
datalog = []
timer = 0
pot = 0
temp = 0
light = 0

def re(channel1):													   	   #functions that are called
    global Reset                                                            #when the event/interrupt occurs
    Reset = True
    
def freq(channel):
    global delay
    if delay<2:
        delay = delay*2
    else:
        delay = 0.5
    print("Current Frequency:", delay, "s")

def stop(channel):
    global monitor
    monitor = not monitor

def disp(channel):
    print("\n|Time     |Timer     |Pot   |Temp  |Light")
    print("-------------------------------------------")
    for i in reversed(range(len(datalog))):
        print(datalog[i])

def GetData(channel):											           #ADC data collection function
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]
    return data

def ConvertVolts(data, places):
    volts = (data*3.3)/float(1023)
    volts = round(volts,places)
    return volts

def Timer(timer):
    hours, rem = divmod(timer, 3600)
    minutes, seconds = divmod(rem, 60)
    return "{:0>2}:{:0>2}:{05.2f}".format(int(hours),int(minutes),seconds)

GPIO.add_event_detect(reset, GPIO.RISING, callback=re, bouncetime=200)		

GPIO.add_event_detect(frequency, GPIO.RISING, callback=freq, bouncetime=200)

GPIO.add_event_detect(stopbtn, GPIO.RISING, callback=stop, bouncetime=200)

GPIO.add_event_detect(display, GPIO.RISING, callback=disp, bouncetime=200)

try:                                                                       #try/except conditional for ADC data collection.
    while True:  
        if monitor:
            pot = ConvertVolts(GetData(potChan), 1)
            temp = int(ConvertVolts(GetData(tempChan), 2)-0.5)*100)
            light = int(ConvertVolts(GetData(ldrChan), 2)*50)
            if light>100:
                light=100
        ctime = datetime.datetime.now().strftime('%H:%M:%S')
        if Reset:
            datalog = []
            pot = " 0"
            temp = "  0"
            light = "  0"
            timer = 0
            Reset = False
            carry = True
        tmrstr = Timer(timer)
        cdata = ctime+"\t"+tmrstr+"\t"+str(pot)+" V \t"+str(temp)+" C \t"+str(light)+"%"
        if monitor or carry:
            datalog.insert(0,cdata)
            if carry:
                print("\n|Time     |Timer     |Pot   |Temp  |Light")
                print("-------------------------------------------")
                for i in reversed(range(len(datalog))):
                    print(datalog[i])
                carry=False
        if len(datalog)>5:
            datalog.remove(datalog[5])
        timer = timer+delay
        time.sleep(delay)

except KeyboardInterrupt:
    spi.close()
    GPIO.cleanup()

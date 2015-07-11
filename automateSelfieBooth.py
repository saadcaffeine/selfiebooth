import time
import sys
import RPi.GPIO as GPIO 
import socket
import fcntl
import struct

import subprocess # invoke php
import imp
caffk = imp.load_compiled("caffk", "/home/pi/py_modules/caffk.pyc") #API Keys

from datetime import datetime
from pushbullet import PushBullet
#PushBullet.py by Richard Borcisk https://github.com/randomchars/pushbullet.py

lightStrip = 14
buttSensor = 23
led3 = 16
led2 = 20
led1 = 21
ledStatus = 26
noButts = 1
apiKey = caffk.api_key
GPIO.setmode(GPIO.BCM) 
GPIO.setup(buttSensor, GPIO.IN, GPIO.PUD_DOWN)  # buttSensor goes from 0 to 3.3v
GPIO.setup(lightStrip, GPIO.OUT)
GPIO.setup(led3,GPIO.OUT)
GPIO.setup(led2,GPIO.OUT)
GPIO.setup(led1,GPIO.OUT)
GPIO.setup(24, GPIO.IN, GPIO.PUD_DOWN) #quit trigger 24 goes 0 to 1 3.3v

GPIO.setup(ledStatus, GPIO.OUT)
GPIO.output(ledStatus, 1) # selfie booth running

print datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def selfieCounter():
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def doGram():
	#GPIO.output(lightStrip,1) #activates relay ON
	#handoff to PHP
	subprocess.call("php /home/pi/sb/insta.php", shell=True)
	time.sleep(1)
	#GPIO.output(lightStrip,0) #activates relay ON	
def takeSelfie():
		GPIO.output(led3,0) #LED 3 OFF
		GPIO.output(led2,1) #LED 2 ON
		time.sleep(1)
		GPIO.output(led2,0) #LED 2 OFF
		GPIO.output(led1,1) #LED 1 ON
		time.sleep(0.6)
		GPIO.output(led1,0)
		time.sleep(0.2)
		GPIO.output(led1,1)
		time.sleep(0.4)
		GPIO.output(led1,0)
		time.sleep(0.2)
		GPIO.output(led1,1)
		time.sleep(0.4)
		GPIO.output(led1,0) #LED 1 OFF
		time.sleep(0.1)
		GPIO.output(lightStrip,1) #activates relay ON
		#using USB camera via fswebcam
		time.sleep(0.4)
		print("selfie ") 
		subprocess.call("fswebcam -r 640x480 --no-banner --save /home/pi/sb/selfie.jpg", shell = True)
		print selfieCounter()
    		GPIO.output(lightStrip,0) #activates relay OFF
def initButt():
		GPIO.output(led3,1) #LED ON
		time.sleep(0.2)	
		GPIO.output(led3,0) #LED OFF
		time.sleep(0.2)
		GPIO.output(led3,1) #LED ON
		time.sleep(0.4)

def testButt():
		initButt()
		GPIO.output(lightStrip,1) #activates relay ON
		time.sleep(2)
		GPIO.output(lightStrip,0) #activates relay Off
		GPIO.output(led3,0) #LED Off
		time.sleep(0.2)	
		GPIO.output(led2,0) #LED Off
		time.sleep(0.2)
		GPIO.output(led1,0) #LED Off

def pushNotification(message):
	try:
		p = PushBullet(apiKey)
		myPhone = p.devices[0]
		myPhone.push_note(message, message)
	except: #todo: gracefully handle exceptions, wouldya
		e = sys.exc_info()[0]	
		print(e)

def pushSelfie(message):
	try:
		p = PushBullet(apiKey)
		myPhone = p.devices[0]
		print("uploading")
		with open('/home/pi/sb/selfie.jpg', "rb") as pic:
			file_data = p.upload_file(pic,"selfie.jpg")
		file_data = str(file_data)
		fileURL = file_data[file_data.find("https"):file_data.find("'})")]
		print (fileURL)
		myPhone.push_file(file_url=fileURL,file_name="selfie.jpg",file_type="image/jpeg")
	except: #todo: gracefully handle exceptions, wouldya
                e = sys.exc_info()[0]
                print(e)

def buttCallback(channel):
	global noButts
	time.sleep(1)
	if(noButts):
		print "butt gone. fine. be that way."
	else:
		initButt()
		print str(channel) + ": " + selfieCounter() 
		time.sleep(1)
		takeSelfie()
		doGram()
		pushNotification("#selfied " + selfieCounter())
		
def haltCallback(channel):
	print "Rising edge detected on port 24. Here endeth the lesson."  
	GPIO.cleanup()           # clean up GPIO on normal exit 

# uses threaded callback
GPIO.add_event_detect(buttSensor, GPIO.RISING, callback=buttCallback, bouncetime=1800)
GPIO.add_event_detect(24, GPIO.RISING, callback=haltCallback)

#init

#except KeyboardInterrupt:
try:  
    testButt()
    pushNotification("SelfieBooth UP! " + " " + selfieCounter())

    while(1):
	#loops until keybaord interrupt or haltCallback
	if(GPIO.input(buttSensor)):
		noButts = 0
	else:
		noButts = 1
    	time.sleep(0.5)
except KeyboardInterrupt:  
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit  
GPIO.cleanup()           # clean up GPIO on normal exit 

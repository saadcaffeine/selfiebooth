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
#selfieCounter = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
apiKey = caffk.api_key
GPIO.setmode(GPIO.BCM) 
GPIO.setup(buttSensor, GPIO.IN, GPIO.PUD_DOWN)  # buttSensor goes from UP to 3.3v
GPIO.setup(lightStrip, GPIO.OUT)
GPIO.setup(led3,GPIO.OUT)
GPIO.setup(led2,GPIO.OUT)
GPIO.setup(led1,GPIO.OUT)
GPIO.setup(24, GPIO.IN, GPIO.PUD_DOWN) #quit trigger 24 goes 0 to 1 3.3v
down = 0


def selfieCounter():
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def doGram():
	#photo = open('/var/www/selfies/selfie.jpg', 'rb')
	#handoff to PHP
	subprocess.call("php /home/sb/insta.php", shell=True)

def get_ip(ifname):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    	return socket.inet_ntoa(fcntl.ioctl(
        	s.fileno(), 0x8915,  # SIOCGIFADDR
        	struct.pack('256s', ifname[:15])
	)[20:24])

def takeSelfie():
		GPIO.output(led3,0) #LED OFF
		time.sleep(1)
		GPIO.output(led2,0) #LED OFF
		time.sleep(1)
		GPIO.output(led1,0) #LED OFF
		time.sleep(1)
		GPIO.output(lightStrip,1) #activates relay ON
		#using USB camera via fswebcam
		print("selfie ") 
		subprocess.call("fswebcam -r 640x480 --save /home/pi/sb/selfie.jpg", shell = True)
		print selfieCounter()
    		GPIO.output(lightStrip,0) #activates relay OFF
def initButt():
		GPIO.output(led3,1) #LED ON
		time.sleep(0.2)	
		GPIO.output(led2,1) #LED ON
		time.sleep(0.2)
		GPIO.output(led1,1) #LED ON

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
	#only if rising. else ignore.
	global down
	if(down):
		print "butt gone"
		down = 0
	else:
		down = 1
		initButt()
		print "BUTT!"
		print str(channel) + ": " + selfieCounter() 
		time.sleep(1)
		takeSelfie()

def falseCallback(channel):
	print "false"

#TODO: init self test
# get IP, push it out
#wip = get_ip('wlan0')
#pushNotification("SelfieBooth UP! " + " " + selfieCounter())

# uses threaded callback
GPIO.add_event_detect(buttSensor, GPIO.RISING, callback=buttCallback, bouncetime=1200)
#GPIO.add_event_detect(buttSensor, GPIO.FALLING, callback=falseCallback)

#init


#except KeyboardInterrupt:
try:  
    print "Waiting for rising edge on port 24"  
    GPIO.wait_for_edge(24, GPIO.RISING)  
    print "Rising edge detected on port 24. Here endeth the lesson."  
  
except KeyboardInterrupt:  
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit  
GPIO.cleanup()           # clean up GPIO on normal exit 



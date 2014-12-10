import time
import picamera
import sys
import RPi.GPIO as GPIO 
import socket
import fcntl
import struct

import subprocess # invoke php

from datetime import datetime
from pushbullet import PushBullet
#PushBullet.py by Richard Borcisk https://github.com/randomchars/pushbullet.py

lightStrip = 25
buttSensor = 24
selfieCounter = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
apiKey = "v1Cixwqg0LImGW3awI1kqIZaHMZNefjMnNujz0roMVkke" #saads pushBullet

GPIO.setmode(GPIO.BCM) 
GPIO.setup(buttSensor, GPIO.IN, GPIO.PUD_DOWN)  # buttSensor PUD UP
GPIO.setup(lightStrip, GPIO.OUT)

def doGram():
	#photo = open('/var/www/selfies/selfie.jpg', 'rb')
	#handoff to PHP
	subprocess.call("php /home/pi/selfiebooth/insta.php", shell=True)

def get_ip(ifname):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    	return socket.inet_ntoa(fcntl.ioctl(
        	s.fileno(), 0x8915,  # SIOCGIFADDR
        	struct.pack('256s', ifname[:15])
	)[20:24])

def takeSelfie():
	with picamera.PiCamera() as camera:
		camera.led = False
    		GPIO.output(lightStrip,1)
    		camera.resolution = (800, 800)
    		camera.framerate = 30
		camera.led = True
#TODO: sound click!
		camera.capture('/var/www/selfies/selfie.jpg')
#		camera.capture('/var/www/selfies/selfie0.jpg') # todo: parameterize 
#TODO: trigger async
		camera.led = False
		print("selfie " + str(selfieCounter))
    		GPIO.output(lightStrip,0)

def pushNotification(message):
	try:
		p = PushBullet(apiKey)
		# Saads iPhone is 0 ujz0roMVkkesjAhkLxzKEK Saadsi4e
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
		with open('/var/www/selfies/selfie.jpg', "rb") as pic:
			file_data = p.upload_file(pic,"selfie.jpg")
		file_data = str(file_data)
		fileURL = file_data[file_data.find("https"):file_data.find("'})")]
		print (fileURL)
		myPhone.push_file(file_url=fileURL,file_name="selfie.jpg",file_type="image/jpeg")
	except: #todo: gracefully handle exceptions, wouldya
                e = sys.exc_info()[0]
                print(e)

#TODO: init self test
# get IP, push it out
wip = get_ip('wlan0')
pushNotification("SelfieBooth UP! " + wip + " " + str(selfieCounter))
takeSelfie()
pushNotification("selfied " + str(selfieCounter))
doGram()
pushSelfie(selfieCounter)
	
# Loop forever
while True:
	GPIO.wait_for_edge(buttSensor, GPIO.RISING)  # butt on
	print("butt on")
	takeSelfie()
	pushNotification("snap! " + str(selfieCounter))
	time.sleep(5); # simulate upload
	while (GPIO.input(buttSensor)):
		#wait for butt to go away
		time.sleep(3);
	#GPIO.wait_for_edge(buttSensor, GPIO.FALLING) # butt off
	print("butt off")
	#smooth out jitters
	#pending buttSensor 
	GPIO.cleanup(buttSensor)
	GPIO.setup(buttSensor, GPIO.IN, GPIO.PUD_DOWN)
		
#looop
#except KeyboardInterrupt:
GPIO.cleanup()

import time
import picamera
import sys
import RPi.GPIO as GPIO 
from datetime import datetime

lightStrip = 25
buttSensor = 24
selfieCounter = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

GPIO.setmode(GPIO.BCM) 
GPIO.setup(buttSensor, GPIO.IN, GPIO.PUD_DOWN)  # buttSensor PUD UP
GPIO.setup(lightStrip, GPIO.OUT)

def takeSelfie():
	with picamera.PiCamera() as camera:
		camera.led = False
    		camera.start_preview() # look at the little red light
    		camera.led = False
    		GPIO.output(lightStrip,1)
    		camera.resolution = (1280, 1280)
    		camera.framerate = 30
		camera.led = True
		camera.capture('/var/www/selfies/selfie.jpg') # todo: parameterize 
    		#todo: trigger php
		camera.led = False
		camera.led = True
		camera.led = False
		#selfieCounter += 1
		print("selfie " + str(selfieCounter))
    		camera.stop_preview()
    		GPIO.output(lightStrip,0)

def pushNotification(message):
	import httplib, urllib
	conn = httplib.HTTPSConnection("api.pushover.net:443")
	try:
		conn.request("POST", "/1/messages.json",
  		urllib.urlencode({
    			"token": "aED986wxM97oLAoL2ptR4A1vmj8hXd",
    			"user": "u1M9FWze6iHWQUvDudYsiK4PbmjXZW",
    			"message": message,
  			}), { "Content-type": "application/x-www-form-urlencoded" })
  		conn.getresponse()
	except:
		#todo: gracefully handle exceptions, wouldya
		e = sys.exc_info()[0]	
		print(e)

# init test
pushNotification("Started UP! " + str(selfieCounter))
takeSelfie()
# Loop forever
while True:
	GPIO.wait_for_edge(buttSensor, GPIO.RISING)  # butt on
	print("butt on")
	takeSelfie()
	pushNotification("selfie " + str(selfieCounter))
	time.sleep(5); # simulate upload
	while (GPIO.input(buttSensor)):
		#wait for butt to go away
		time.sleep(3);
	#GPIO.wait_for_edge(buttSensor, GPIO.FALLING) # butt off
	print("butt off")
	GPIO.cleanup(buttSensor)
	GPIO.setup(buttSensor, GPIO.IN, GPIO.PUD_DOWN)
		
#looop
#except KeyboardInterrupt:
GPIO.cleanup()

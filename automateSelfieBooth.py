import time
import picamera
import sys
import RPi.GPIO as GPIO 
from twython import Twython
from datetime import datetime

lightStrip = 25
buttSensor = 24
selfieCounter = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
APP_KEY = 'YOUR_APP_KEY'
APP_SECRET = 'YOUR_APP_SECRET'
ACCESS_TOKEN = ' '

GPIO.setmode(GPIO.BCM) 
GPIO.setup(buttSensor, GPIO.IN, GPIO.PUD_DOWN)  # buttSensor PUD UP
GPIO.setup(lightStrip, GPIO.OUT)

def initTwit():
	twit = Twython(APP_KEY, APP_SECRET, oauth_version=2)
	ACCESS_TOKEN = twitter.obtain_access_token()
	#handle exceptions

def doTwit()
	photo = open('/var/www/selfies/selfie.jpg', 'rb')
	twitter.update_status_with_media(status='butt activated selfie ', media=photo)

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
	#smooth out jitters
	#pending buttSensor 
	GPIO.cleanup(buttSensor)
	GPIO.setup(buttSensor, GPIO.IN, GPIO.PUD_DOWN)
		
#looop
#except KeyboardInterrupt:
GPIO.cleanup()

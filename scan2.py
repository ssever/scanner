from bluepy.btle import Scanner, DefaultDelegate
from datetime import datetime
import time
import json
import threading
import logging
import requests


LOG_LEVEL = logging.INFO
beacons = {}
beacon_value = 0
power_limiter = -75
scanner_id = "laptop"
#LOG_LEVEL = logging.DEBUG
LOG_FILE = "/home/ss/wifiloc"
#LOG_FILE = "/dev/stdout"
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, level=LOG_LEVEL)

from threading import Timer

def hello(name):
	print "Sending to server : %s!" % name
	url = "http://client.mdphotoapp.com/estetik/raspi_proloc.php?scanner=%s" % scanner_id
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	r = requests.post(url, data=json.dumps(beacons), headers=headers)
	print(r.text) #TEXT/HTML
	print(r.status_code, r.reason) #HTTP
	beacons.clear()

class RepeatedTimer(object):
  def __init__(self, interval, function, *args, **kwargs):
    self._timer = None
    self.interval = interval
    self.function = function
    self.args = args
    self.kwargs = kwargs
    self.is_running = False
    self.next_call = time.time()
    self.start()

  def _run(self):
    self.is_running = False
    self.start()
    self.function(*self.args, **self.kwargs)

  def start(self):
    if not self.is_running:
      self.next_call += self.interval
      self._timer = threading.Timer(self.next_call - time.time(), self._run)
      self._timer.start()
      self.is_running = True

  def stop(self):
    self._timer.cancel()
    self.is_running = False

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    #def handleDiscovery(self, dev, isNewDev, isNewData):
        #if isNewDev:
            #print "Discovered device", dev.addr
        #if isNewData:
            #print "Received new data from", dev.addr

rt = RepeatedTimer(60, hello, "World")
try:
    while True:
        scanner = Scanner().withDelegate(ScanDelegate())
	devices = scanner.scan(10)

	for dev in devices:
		if dev.addr.find("ff:ff") == 0 and dev.rssi > power_limiter:
			logging.info("%s RSSI=%d dB" % (dev.addr, dev.rssi))
			if beacons.has_key(dev.addr):
				beacon_value = int((beacons[dev.addr]+dev.rssi)/2)
				beacons[dev.addr] = beacon_value
			else:
				beacons[dev.addr] = dev.rssi

			print time.strftime("%H:%M:%S")," : %s RSSI=%d dB Sum: %d" % (dev.addr, dev.rssi,beacon_value)
			
    			#for (adtype, desc, value) in dev.getScanData():
        		#print "  %s = %s" % (desc, value)
except KeyboardInterrupt:
	rt.stop()
	pass

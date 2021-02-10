import network
import machine
import config
from time import sleep,sleep_ms

def do_connect():
  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  if not wlan.isconnected():
    wlan.connect(config.WLAN_SSID,config.WLAN_PASS)
    while not wlan.isconnected():
      sleep_ms(50)
      pass
  print('network config:', wlan.ifconfig())

def do_disconnect():
  wlan = network.WLAN(network.STA_IF)
  wlan.disconnect()
  wlan.active(False)

# WLAN connection
if config.WLAN_ENABLE is True:
  do_connect()

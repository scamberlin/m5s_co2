# Display driver from https://github.com/russhughes/ili9342c_mpy
import config
import network
import time
import utime
import machine
import ili9342c
import adafruit_sgp30
import vga1_8x16 as font1
import vga1_bold_16x32 as font2
import random
import _thread
import ntptime
import utime

from time import sleep
from machine import SoftI2C, Pin, RTC

try:
  from umqtt.robust import MQTTClient
except Exception as e:
  print("Exception: {}".format(e))

def get_address():
  if config.WLAN_ENABLE is False:
    return None
  try:
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
      return 'none'
    return wlan.ifconfig()[0]
  except Exception as e:
    print("Exception: {}".format(e))

def get_broker_address():
  return config.MQTT_BROKER

def _time():
  while True:
    gmt = rtc.datetime()    # get the date and time in UTC
    date = '{:02}/{:02}/{:02}'.format(gmt[0], gmt[1], gmt[2])
    time = '{:02}:{:02}:{:02}'.format(gmt[4], gmt[5], gmt[6])
    tft.text(font1, time, 0, 0, ili9342c.WHITE, ili9342c.BLACK)
    tft.text(font1, date, tft.width() - (font1.WIDTH * len(date)), 0, ili9342c.WHITE, ili9342c.BLACK)
    utime.sleep(1)

def _network():
  while True:
    tft.text(font1, "ip: {:.15}".format(get_address()), 0, h - (font1.HEIGHT+2), ili9342c.WHITE, ili9342c.BLACK)
    tft.text(font1, "dst: {:.15}".format(get_broker_address()), tft.width() - (font1.WIDTH * (len(get_broker_address()) +5)), h - (font1.HEIGHT+2), ili9342c.WHITE, ili9342c.BLACK)
    utime.sleep(10)

def _gaz():
  while True:
    co2_eq, tvoc = sgp30.iaq_measure()
    print('co2eq = ' + str(co2_eq) + ' ppm \t tvoc = ' + str(tvoc) + ' ppb')
    co2_color = ili9342c.YELLOW
    if co2_eq >= 1200:
      co2_color = ili9342c.RED
    elif co2_eq < 850:
      co2_color = ili9342c.GREEN
    tvoc_color = ili9342c.YELLOW
    if tvoc > 2000:
      tvoc_color = ili9342c.RED
    elif tvoc < 600:
      tvoc_color = ili9342c.GREEN
    tft.text(font2, "CO2 -> {:.10} ppm".format(co2_eq), 20, 50, co2_color, ili9342c.BLACK)
    tft.text(font2, "TVOC -> {:.10} ppb".format(tvoc), 20, 150, tvoc_color, ili9342c.BLACK)
    if config.MQTT_ENABLE is True and config.WLAN_ENABLE is True:
      payload = b'{"location":"' + config.LOCATION + '","ppm":' + str(co2_eq) + ',"ppb":' + str(tvoc) + '}'
      try:
        mqc.connect()
        mqc.publish(b""+config.MQTT_TOPIC,payload)
        print("MQTT: publish co2({})/tvoc({}) to {}".format(co2_eq, tvoc, config.MQTT_BROKER))
        mqc.disconnect()
      except Exception as e:
        print("Exception: {}".format(e))
    utime.sleep(5)

# setting NTP time
try :
  rtc = RTC()
  ntptime.settime()
except Exception as e:
  print("Exception: {}".format(e))

# scanning I2C bus
try:
  i2c = SoftI2C(
    sda=machine.Pin(21),
    scl=machine.Pin(22),
    freq=100000) # valid for M5Stack grey and basic
  devices = i2c.scan()
  if len(devices) == 0:
    print("Error: no I2C device !")
  else:
    for d in devices:
      print("Decimal address: ",d," | Hexa address: ",hex(d))
except Exception as e:
  print("Exception: {}".format(e))

# init SGP30
try:
  co2_eq = 400
  tvoc = 0
  sgp30 = adafruit_sgp30.Adafruit_SGP30(
    i2c,
    address=0x58)
  print("SGP30 serial #", [hex(i) for i in sgp30.serial])
  sgp30.iaq_init()
  print("Waiting 5 seconds for SGP30 initialization.")
  time.sleep(1)
except Exception as e:
  print("Exception: {}".format(e))

# init SPI
try:
  spi = machine.SPI(
    2,
    baudrate=40000000,
    polarity=1,
    phase=1,
    sck=Pin(18),
    mosi=Pin(23))
  tft = ili9342c.ILI9342C(
    spi,
    320,
    240,
    reset=Pin(33, Pin.OUT),
    cs=Pin(14, Pin.OUT),
    dc=Pin(27, Pin.OUT),
    backlight=Pin(32, Pin.OUT),
    rotation=0)
  tft.init()
  tft.fill(ili9342c.BLACK)
  w = tft.width()
  h = tft.height()
  tft.hline(0, 20, w, ili9342c.WHITE)
  tft.hline(0, 120, w, ili9342c.WHITE)
  tft.hline(0, 215, w, ili9342c.WHITE)
except Exception as e:
  print("Exception: {}".format(e))

# MQTT init
try:
  if config.MQTT_ENABLE is True and config.WLAN_ENABLE is True:
    mqc = MQTTClient("umqtt_client_"+config.LOCATION,server=b'{}'.format(config.MQTT_BROKER),port=1883,ssl=False)
except Exception as e:
  print("Exception: {}".format(e))

# Start thread
_thread.start_new_thread(_network,())
_thread.start_new_thread(_time,())
_thread.start_new_thread(_gaz,())

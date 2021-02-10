.DEFAULT_GOAL = help

help:
	@echo "---------------HELP-----------------"
	@echo "To erase flash type make erase"
	@echo "To flash firmware type make flash"
	@echo "To push code type make all"
	@echo "To moniror device type make console"
	@echo "To join type make run"
	@echo "------------------------------------"

PORT = /dev/ttyUSB0
SPEED = 115200
CHIPSET = esp32
FIRMWARE = firmware/esp32-idf4--20210203-v1.14_ili9342c_mpy.bin
BIN = ${HOME}/python/venv/bin/
FONTS_BITMAP = fonts/bitmap
ESPTOOL = esptool.py
AMPY = ampy
RSHELL = rshell

flash:
	$(BIN)$(ESPTOOL) --chip $(CHIPSET) --port $(PORT) --baud 750000 write_flash -z 0x1000 $(FIRMWARE)

boot: boot.py
	$(BIN)$(AMPY) -p $(PORT) put $<

main: main.py
	$(BIN)$(AMPY) -p $(PORT) put $<

lib: lib/*
	$(BIN)$(AMPY) -p $(PORT) mkdir lib
	$(BIN)$(AMPY) -p $(PORT) mkdir lib/umqtt

fonts_bitmap: $(FONTS_BITMAP)/*
	$(BIN)$(AMPY) -p $(PORT) put fonts/bitmap/vga1_16x16.py lib/vga1_16x16.py
	$(BIN)$(AMPY) -p $(PORT) put fonts/bitmap/vga1_16x32.py lib/vga1_16x32.py
	$(BIN)$(AMPY) -p $(PORT) put fonts/bitmap/vga1_8x16.py lib/vga1_8x16.py
	$(BIN)$(AMPY) -p $(PORT) put fonts/bitmap/vga1_8x8.py lib/vga1_8x8.py
	$(BIN)$(AMPY) -p $(PORT) put fonts/bitmap/vga1_bold_16x16.py lib/vga1_bold_16x16.py
	$(BIN)$(AMPY) -p $(PORT) put fonts/bitmap/vga1_bold_16x32.py lib/vga1_bold_16x32.py

config: config.py
	$(BIN)$(AMPY) -p $(PORT) put $<

umqtt: lib/umqtt/*
	$(BIN)$(AMPY) -p $(PORT) put lib/umqtt/simple.py lib/umqtt/simple.py
	$(BIN)$(AMPY) -p $(PORT) put lib/umqtt/robust.py lib/umqtt/robust.py

sgp30: lib/adafruit_sgp30.py
	$(BIN)$(AMPY) -p $(PORT) put lib/adafruit_sgp30.py lib/adafruit_sgp30.py

all: umqtt sgp30 fonts_bitmap config main boot

rshell:
	$(BIN)$(RSHELL) --buffer-size=30 -p $(PORT)

console:
	pyserial-miniterm $(PORT) $(SPEED)

erase:
	$(ESPTOOL) --chip $(CHIPSET) --port $(PORT) erase_flash

run: all console

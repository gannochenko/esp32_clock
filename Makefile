ls_dev:
#	mpremote connect list | grep modem
	ls /dev/tty* | grep modem

# insert here what the "ls_dev" found:
PORT = /dev/cu.usbmodem101

erase_flash:
	esptool.py --chip esp32s3 --port $(PORT) erase-flash

flash_mp:
	esptool.py --chip esp32s3 --port $(PORT) --baud 460800 write_flash -z 0x0  ./micropython/ESP32_GENERIC_S3-20250911-v1.26.1.bin

run_stat:
	mpremote connect $(PORT) run util/stat.py

run_scandev:
	mpremote connect $(PORT) run util/scandev.py

# repl:
# 	mpremote connect $(PORT)

mount:
	mpremote mount ./src

reset:
	mpremote reset

run:
	mpremote mount ./src run src/main.py

run_ui:
	mpremote mount ./src run src/render_ui.py

deploy:
	mpremote cp -r src/* :

undeploy:
	mpremote rm :main.py # prevent auto-run on reset
	mpremote reset
	$(MAKE) erase_flash
	$(MAKE) flash_mp

ls:
	mpremote ls

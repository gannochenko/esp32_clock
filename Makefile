ls_dev:
	ls /dev/tty* | grep modem

# insert here what the "ls_dev" found:
PORT = /dev/tty.usbmodem101

erase_flash:
	esptool.py --chip esp32s3 --port $(PORT) erase-flash

flash_mp:
	esptool.py --chip esp32s3 --port $(PORT) --baud 460800 write_flash -z 0x0  ./micropython/ESP32_GENERIC_S3-20250911-v1.26.1.bin

install_ssd1306:
	curl -o micropython/ssd1306.py https://raw.githubusercontent.com/micropython/micropython-lib/master/micropython/drivers/display/ssd1306/ssd1306.py
	mpremote cp micropython/ssd1306.py :ssd1306.py

install_fonts:
	curl -o micropython/freesans20.py https://raw.githubusercontent.com/peterhinch/micropython-font-to-py/master/writer/freesans20.py
	curl -o micropython/font10.py https://raw.githubusercontent.com/peterhinch/micropython-font-to-py/master/writer/font10.py
	curl -o micropython/font6.py https://raw.githubusercontent.com/peterhinch/micropython-font-to-py/master/writer/font6.py
	curl -o micropython/writer.py https://raw.githubusercontent.com/peterhinch/micropython-font-to-py/master/writer/writer.py
	mpremote cp micropython/freesans20.py :freesans20.py
	mpremote cp micropython/font10.py :font10.py
	mpremote cp micropython/font6.py :font6.py
	mpremote cp micropython/writer.py :writer.py

run_stat:
	mpremote connect $(PORT) run util/stat.py

run_reset:
	mpremote reset

run_scandev:
	mpremote connect $(PORT) run util/scandev.py

run_screentest:
	mpremote connect $(PORT) run util/screen_test.py

run_ui:
	mpremote connect $(PORT) run util/ui.py

repl:
	mpremote connect $(PORT)

mount:
	mpremote mount ./src

run:
	mpremote mount ./src run src/main.py

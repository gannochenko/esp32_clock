# boot.py -- run on boot to configure USB and filesystem
import machine
import gc

# Disable WiFi on boot to save power (can be enabled later if needed)
import network
sta_if = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)
sta_if.active(False)
ap_if.active(False)

# Run garbage collection
gc.collect()

print("Boot sequence complete")

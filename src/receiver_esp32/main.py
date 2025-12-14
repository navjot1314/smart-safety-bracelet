"""
Smart Safety Bracelet – Receiver Firmware
Target Device: ESP32

Function:
- Receives SOS and GPS location data via LoRa
- Processes incoming messages from the bracelet
- Can be extended to trigger alerts or logging

Note:
This is prototype firmware developed for learning and testing purposes.
"""
from machine import Pin, SPI
import time
from sx127xhub import SX1278Hub  # Your fixed driver

# ----------------------------
# SPI & Hub Initialization
# ----------------------------
spi = SPI(1, baudrate=5000000, polarity=0, phase=0,
          sck=Pin(18), mosi=Pin(23), miso=Pin(19))

# Initialize hub with proper pins
hub = SX1278Hub(spi, cs_pin=5, reset_pin=14, dio0_pin=26, frequency=433E6)

print("✅ Hub ready, waiting for SOS packets...")

# ----------------------------
# Helper: read IRQ flags directly
# ----------------------------
REG_IRQ_FLAGS = 0x12
IRQ_RX_DONE = 0x40

# ----------------------------
# Main loop: poll IRQ flags
# ----------------------------
while True:
    irq = hub.read_reg(REG_IRQ_FLAGS)
    if irq & IRQ_RX_DONE:
        pkt = hub.receive()
        hub.write_reg(REG_IRQ_FLAGS, 0xFF)  # Clear IRQ flags

        if pkt:
            try:
                msg = pkt.decode('utf-8').strip()
                print("Received:", msg)

                # Optional: parse GPS coordinates
                if msg.startswith("SOS"):
                    parts = msg.split(',')
                    lat = parts[1].split(':')[1].strip()
                    lon = parts[2].split(':')[1].strip()
                    print("→ Latitude:", lat, "Longitude:", lon)

            except Exception as e:
                print("Decode error:", e)

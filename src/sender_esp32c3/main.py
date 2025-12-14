"""
Smart Safety Bracelet – Sender Firmware
Target Device: ESP32-C3

Function:
- Reads GPS location data
- Sends SOS and location information via LoRa to receiver
- Triggered by emergency button press

Note:
This is prototype firmware developed for learning and testing purposes.
"""
from machine import UART, SPI, Pin
import time
from sx127x import SX127x  # Use the patched driver with bytearray support

# ===============================
# GPS CLASS
# ===============================
class GPS:
    def __init__(self, tx_pin=0, rx_pin=2, baudrate=9600):
        self.uart = UART(1, tx=tx_pin, rx=rx_pin, baudrate=baudrate)
        self.fix_acquired = False

    def read(self):
        """Read GPS data. Returns (lat, lon) if fix acquired, else None"""
        if self.uart.any():
            line = self.uart.readline()
            if line:
                try:
                    line_str = line.decode('utf-8').strip()
                    print("GPS Raw:", line_str)

                    if line_str.startswith("$GPGGA"):
                        parts = line_str.split(",")
                        fix_quality = int(parts[6])  # Field 6 = fix quality
                        if fix_quality == 0:
                            self.fix_acquired = False
                            return None
                        if len(parts) > 5 and parts[2] and parts[4]:
                            lat = self._convert_to_degrees(parts[2])
                            lon = self._convert_to_degrees(parts[4])
                            if not self.fix_acquired:
                                print("✅ GPS Fix Acquired!")
                                self.fix_acquired = True
                            return lat, lon
                except Exception as e:
                    print("GPS Parse Error:", e)
        return None

    def _convert_to_degrees(self, raw_value):
        raw_value = float(raw_value)
        degrees = int(raw_value / 100)
        minutes = raw_value - degrees * 100
        return degrees + minutes / 60.0

# ===============================
# LORA SETUP
# ===============================
lora_pins = {
    'ss': 10,      # Chip select GPIO
    'reset': 3,    # Reset GPIO
    'dio0': 1,     # DIO0 GPIO
    'sck': 2,      # SPI SCK
    'mosi': 3,     # SPI MOSI
    'miso': 4      # SPI MISO
}

spi = SPI(1, baudrate=1000000,
          polarity=0, phase=0,
          sck=Pin(lora_pins['sck']),
          mosi=Pin(lora_pins['mosi']),
          miso=Pin(lora_pins['miso']))

lora = SX127x(
    spi,
    pins={
        'ss': lora_pins['ss'],
        'reset': lora_pins['reset'],
        'dio0': lora_pins['dio0']
    },
    parameters={
        'frequency': 433E6,
        'tx_power_level': 17,
        'signal_bandwidth': 125E3,
        'spreading_factor': 7,
        'coding_rate': 5
    }
)

# ===============================
# MAIN LOOP
# ===============================
gps = GPS(tx_pin=0, rx_pin=2)   # Neo-6M: TX->D0, RX->D2
last_coords = None

print("✅ Bracelet LoRa + GPS Ready")

while True:
    coords = gps.read()
    
    if coords:
        last_coords = coords  # store last valid fix
        lat, lon = last_coords
        msg = "SOS, Lat:{:.6f}, Lon:{:.6f}".format(lat, lon)
        print("Sending:", msg)
        lora.println(msg)
    else:
        if last_coords:
            # send last known coordinates until new fix
            lat, lon = last_coords
            msg = "SOS, Lat:{:.6f}, Lon:{:.6f}".format(lat, lon)
            print("Sending last known coordinates:", msg)
            lora.println(msg)
        else:
            print("Waiting for GPS fix...")

    time.sleep(5)


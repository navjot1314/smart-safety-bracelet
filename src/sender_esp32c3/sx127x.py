"""
LoRa Driver Module
Used by sender firmware (ESP32-C3)

Handles:
- LoRa module initialization
- Packet transmission
"""
from machine import Pin, SPI
import time

# SX1278 Registers
REG_FIFO = 0x00
REG_OP_MODE = 0x01
REG_FRF_MSB = 0x06
REG_FRF_MID = 0x07
REG_FRF_LSB = 0x08
REG_FIFO_ADDR_PTR = 0x0D
REG_FIFO_RX_BASE = 0x0F
REG_FIFO_TX_BASE = 0x0E
REG_IRQ_FLAGS = 0x12
REG_RX_NB_BYTES = 0x13
REG_FIFO_RX_CURRENT = 0x10
REG_PAYLOAD_LENGTH = 0x22

MODE_SLEEP = 0x00
MODE_STDBY = 0x01
MODE_RXCONT = 0x05
MODE_TX = 0x03

class SX1278Hub:
    def __init__(self, spi, cs_pin, reset_pin, dio0_pin, frequency=433E6):
        self.spi = spi
        self.cs = Pin(cs_pin, Pin.OUT, value=1)
        self.reset = Pin(reset_pin, Pin.OUT, value=1)
        self.dio0 = Pin(dio0_pin, Pin.IN)

        # Reset LoRa
        self.reset.value(0)
        time.sleep(0.01)
        self.reset.value(1)
        time.sleep(0.01)

        # Sleep mode
        self.write_reg(REG_OP_MODE, MODE_SLEEP)
        self.set_frequency(frequency)
        # FIFO base
        self.write_reg(REG_FIFO_RX_BASE, 0x00)
        self.write_reg(REG_FIFO_TX_BASE, 0x80)
        # Standby
        self.write_reg(REG_OP_MODE, MODE_STDBY)

    def write_reg(self, reg, val):
        self.cs.value(0)
        self.spi.write(bytearray([reg | 0x80, val]))
        self.cs.value(1)

    def read_reg(self, reg):
        self.cs.value(0)
        self.spi.write(bytearray([reg & 0x7F]))
        val = self.spi.read(1)[0]
        self.cs.value(1)
        return val

    def set_frequency(self, freq):
        frf = int((freq / 32000000) * (1 << 19))
        self.write_reg(REG_FRF_MSB, (frf >> 16) & 0xFF)
        self.write_reg(REG_FRF_MID, (frf >> 8) & 0xFF)
        self.write_reg(REG_FRF_LSB, frf & 0xFF)

    def receive(self):
        # RX continuous mode
        self.write_reg(REG_OP_MODE, MODE_RXCONT)
        if self.dio0.value() == 1:
            irq = self.read_reg(REG_IRQ_FLAGS)
            if irq & 0x40:
                self.write_reg(REG_IRQ_FLAGS, 0xFF)
                cur_addr = self.read_reg(REG_FIFO_RX_CURRENT)
                nb_bytes = self.read_reg(REG_RX_NB_BYTES)
                self.write_reg(REG_FIFO_ADDR_PTR, cur_addr)
                payload = bytearray()
                for _ in range(nb_bytes):
                    payload.append(self.read_reg(REG_FIFO))
                return payload
        return None

from machine import Pin, bitstream, time_pulse_us
from utime import ticks_us, ticks_diff
import gc
import array
import logging

from memory import InboxBuffer, OutboxBuffer
from gpio import LASER_PIN, DETECTOR_PIN, LED_PIN

led = Pin(LED_PIN, Pin.OUT)

gc.disable()

TEST_BITSTREAM = True
# Timing of high-low pulse modulation in machine.bitstream in ns
# (high_time_0, low_time_0, high_time_1, low_time_1)
# (1ms, 3ms, 4ms, 2ms)
# Average bit duration of 5ms -> 200bps data rate
BITSTREAM_TIMING = (1000000, 3000000, 4000000, 2000000)
# BITSTREAM_TIMING = (300000, 700000, 600000, 400000)
BITSTREAM_MAX_PULSE_US = int((BITSTREAM_TIMING[2] + BITSTREAM_TIMING[3]) / 1000)
BITSTREAM_DUR_0 = BITSTREAM_TIMING[0]/1000
BITSTREAM_DUR_1 = BITSTREAM_TIMING[2]/1000

# log = logging.getLogger('lindalaser')

class LindaLaser(object):
    def __init__(self, inbox: InboxBuffer, outbox: OutboxBuffer, 
                 laser_pin: int=LASER_PIN, detector_pin: int=DETECTOR_PIN) -> None:
        self.inbox = inbox
        self.outbox = outbox
        self.tx_toggle = True
        self.rx_flag = False
        self.rx_byte = array.array('i')
        self.rx_chrs = []
        # Init the laser and detector pins
        self._init_pins(laser_pin, detector_pin)
        # log.debug('New LindaLaser created')

    def __repr__(self) -> str:
        return "Laser!"

    def __str__(self) -> str:
        return "Laser"

    def _init_pins(self, laser_pin: int, detector_pin: int) -> None:
        self.laser = Pin(laser_pin, Pin.OUT)
        # The laser sensor modules output LOW when it sees a laser and HIGH otherwise
        self.detector = Pin(detector_pin, Pin.IN, pull=Pin.PULL_UP)
        self.detector.irq(handler=self._rx_bitstream, trigger=Pin.IRQ_FALLING)

    def _toggle_tx(self, tx_toggle: bool) -> None:
        """
        Update the global LindaLaser state to toggle between Tx and Rx

        Args:
            tx_toggle (bool): State toggle boolean. TRUE if Tx, FALSE if Rx
        """
        self.tx_toggle = tx_toggle
        

    def _rx_bitstream(self, irq):
        """
        Callback function triggered on laser detector interrupt. 
        If receiving, time the incoming tick and save its duration to the rx_byte array

        Args:
            irq (irq): Default single-argument of micropython interrupt callbacks
        """
        tick_dur = time_pulse_us(self.detector, 0, BITSTREAM_MAX_PULSE_US)
        # print(tick_dur)
        tick_val = 0 if (abs(tick_dur - BITSTREAM_DUR_0) < abs(tick_dur - BITSTREAM_DUR_1)) else 1
        if self.rx_flag:
            self.rx_byte.append(tick_val)
        led.value(tick_val)    

    def _reset_rx_byte(self):
        self.rx_byte = array.array('i')

    def _transmit_buffer(self, outbox_mv: memoryview, start_idx: int=0, end_idx: int=32) -> None:
        """
        Transmits data in the given memoryview by bit-banging the laser module output using machine.bitstream()
        Uses high-low pulse duration modulation, defined in the global four-tuple BITSTREAM_TIMING

        Args:
            outbox_mv (memoryview): Memoryview of a bytearray() containing data to transmit
            start_idx (int): Index of memoryview byte to begin transmitting
            end_idx (int): Index of memoryview bytes to end transmitting
        """
        bitstream(self.laser, 0, BITSTREAM_TIMING, outbox_mv[start_idx:end_idx])
        gc.collect()
        self.laser.off()

    def transmit_outbox(self, msg_len: int=-1) -> None:
        """
        Transmit the contents of the outbox, optionally choosing the amount of data to transmit.
        If no length argument is given, transmit the entire message

        Args:
            msg_len (int, optional): The length in bytes of the message to send. Defaults to -1,
                which indicates transmission of the entire outbox message.
        """
        if msg_len == 0:
            print('no message to transmit')
        # Get the length of the outbox message
        elif msg_len == -1:
            self._transmit_buffer(self.outbox._msg, end_idx=len(self.outbox))
        else:
            self._transmit_buffer(self.outbox._msg, end_idx=msg_len)

    def start_rx(self, duration: int=5):
        """
        Recieves laser detector input as data for a given duration. Converts incoming bits to byte integers
        and writes to inbox memory buffer
    
        Args:
            duration (int, optional): Duration to listen, in seconds. Defaults to 5.
        """
        # Sometimes junk data gets in the rx_byte before we start the Rx transaction
        # If that's true, reset self.rx_byte
        if len(self.rx_byte) != 0:
            print('resetting')
            self.rx_byte = array.array('i')
        start = ticks_us()
        self.rx_flag = True
        while ticks_diff(ticks_us(), start) < (duration*1000000):
            # Stay in this loop until the Rx transaction has lasted the given duration
            pass
        self.rx_flag = False
        gc.collect()
        if len(self.rx_byte) > 0:
            rx_str = print_rx_byte(self.rx_byte)
            print(rx_str)
            self.inbox._read_ascii(print_rx_byte(self.rx_byte))
            self.rx_byte = array.array('i')
            print("Rx successful!")
        else:
            print("No data was recieved during Rx period")
                    
tl = LindaLaser(InboxBuffer(1024), OutboxBuffer(1024))

def rx_byte_chrs(bit_list):
    chrs = []
    byte_string = ""
    for bit in bit_list:
        byte_string += str(bit)
        if len(byte_string) == 8:
            byte_int = int(byte_string, 2)
            chrs.append(chr(byte_int))
            byte_string = ""

    return chrs

def print_rx_byte(bit_list):
    chrs = rx_byte_chrs(bit_list)
    return ("".join(chrs))
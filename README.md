# LEGO BLE Arduino Controller

A LEGO Education / Arduino project for bridging LE-BT devices and commonly available Arduino peripherals.

## Overview

This project consists of two main components:

1. **Python Script** (`lego_ble_controller.py`): 
Collects data from LE Controller and sneds it on the serial port
Parses data from the Arduino (via Serial port) to control a Double Motor

2. **Arduino Sketch** (`arduino_sketch/lego_controller.ino`): 
Receives serial stream of Controller stick positions to control a pair of NeoPixels.
Reads in the state of a button and Potentiometer and sends via serial port

## Hardware Requirements

- Arduino Uno (or compatible board)
- Neopixels, buttons, potentiometer
- USB cable for Arduino programming and power
- LEGO Education Controller from CSAI kit
- LEGO Education Double Motor from CSAI kit


### Python Dependencies

- Python 3.7+
- bleak (for BLE communication)
- pyserial (for serial communication)

### Arduino Requirements

- Arduino IDE
- Arduino Uno board package


### Starting the Python Application

```bash
python lego_ble_controller.py
```

### Serial Communication Protocol
Python script sends "leftPercent (-100 -> 100), righPercent, /n" as gathered from the LE Controller

Arduino sends "potentiometer analog reading (0->1024), button state (1/0)" gathered from peripherals



## Author

Created May 2026 - Damien Kee

# LEGO BLE Arduino Controller

A Python/Arduino project for controlling LEGO Bluetooth devices through serial communication.

## Overview

This project consists of two main components:

1. **Python Application** (`lego_ble_controller.py`): Communicates with LEGO Bluetooth Low Energy (BLE) devices and sends commands to an Arduino microcontroller via serial port.

2. **Arduino Sketch** (`arduino_sketch/lego_controller.ino`): Receives commands from the Python application and controls LEGO motors/devices accordingly.

## Hardware Requirements

- Arduino Uno (or compatible board)
- USB cable for Arduino programming and power
- LEGO device with Bluetooth support
- PC or Raspberry Pi running Python

## Software Requirements

### Python Dependencies

- Python 3.7+
- bleak (for BLE communication)
- pyserial (for serial communication)

### Arduino Requirements

- Arduino IDE
- Arduino Uno board package

## Installation

### Python Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/lego-csai-arduino.git
cd lego-csai-arduino

# Install Python dependencies
pip install -r requirements.txt
```

### Arduino Setup

1. Open Arduino IDE
2. Open the sketch: `arduino_sketch/lego_controller.ino`
3. Select Board: Arduino Uno
4. Select Port: (your Arduino's COM port)
5. Click Upload

## Usage

### Starting the Python Application

```bash
python lego_ble_controller.py
```

### Serial Communication Protocol

The Arduino accepts commands via serial (9600 baud):

- `MOTOR_A:150` - Set motor A to speed 150 (0-255)
- `MOTOR_B:255` - Set motor B to full speed
- `MOTOR_C:100` - Set motor C to speed 100
- `STOP` - Stop all motors
- `STATUS` - Get current motor status

## Architecture

```
Python Application
    ↓ (BLE)
LEGO Device
    ↑ (commands)
    ↓ (serial)
Arduino Uno
    ↓ (PWM)
LEGO Motors
```

## Project Structure

```
lego-csai-arduino/
├── lego_ble_controller.py     # Main Python BLE controller
├── arduino_sketch/
│   └── lego_controller.ino    # Arduino sketch
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── .gitignore                # Git ignore rules
```

## License

MIT License

## Author

Created May 2026

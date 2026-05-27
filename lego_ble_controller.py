"""Simple LEGO CSAI hardware test runner.

Set the boolean flags below to choose which devices to connect.
The script connects only the selected hardware and runs the matching test.
"""

import time

import legoeducation as le
import serial


CARD_COLOUR = le.LEGO_COLOR_RED
CARD_SERIAL = '0943'
SERIAL_PORT = 'COM7'
SERIAL_BAUDRATE = 9600
SERIAL_TIMEOUT_SECONDS = 1

# Change these booleans to match the hardware you want to test.
CONNECT_DOUBLE_MOTOR = True
CONNECT_CONTROLLER = True



"""Connect to devices that are 'True' flags."""
print("Connecting to devices. Please wait...")

if CONNECT_DOUBLE_MOTOR:
    double_motor = le.DoubleMotor()
    double_motor.connect(card_color=CARD_COLOUR, card_serial=CARD_SERIAL)
    if not double_motor.connected:
        print('Error connecting to Double Motor.')
        exit(1) # error connecting
    print(f"Connected Double Motor")

if CONNECT_CONTROLLER:
    controller = le.Controller()
    controller.connect(card_color=CARD_COLOUR, card_serial=CARD_SERIAL)
    if not controller.connected:
        print('Error connecting to Controller.')
        exit(1) # error connecting
    print(f"Connected Controller")

try:
    arduino_serial = serial.Serial(
        port=SERIAL_PORT,
        baudrate=SERIAL_BAUDRATE,
        timeout=SERIAL_TIMEOUT_SECONDS,
    )
except serial.SerialException as error:
    print(f"Error opening serial port {SERIAL_PORT}: {error}")
    exit(1)

print(f"Serial connected on {SERIAL_PORT} at {SERIAL_BAUDRATE} baud.")


"""Run tests for the connected devices."""
print("Starting tests for connected devices.")

try:
    """Use Arduino serial input speed,button to drive the double motor."""
    print("Running Arduino serial control until Ctrl+C: speed controls left motor, button=1 spins right motor.")

    last_button_state = 0

    while True:
        left_percent = controller.sensor.leftPercent
        right_percent = controller.sensor.rightPercent

        arduino_serial.write(f"{left_percent},{right_percent}\n".encode("ascii"))

        latest_speed_value = None
        latest_button_value = None

        while arduino_serial.in_waiting > 0:
            incoming_message = arduino_serial.readline().decode("ascii", errors="ignore").strip()
            if not incoming_message:
                continue

            parts = incoming_message.split(',')
            if len(parts) != 2:
                continue

            try:
                speed_value = int(parts[0].strip())
                button_value = int(parts[1].strip())
            except ValueError:
                continue

            latest_speed_value = speed_value
            latest_button_value = button_value

        if latest_speed_value is not None and latest_button_value is not None:
            left_speed = int(round((latest_speed_value / 1023.0) * 100))
            double_motor.motor_run(direction=le.MOTOR_MOVE_DIRECTION_COUNTERCLOCKWISE, motor=le.MOTOR_LEFT, speed=left_speed)

            if latest_button_value == 1 and last_button_state == 0:
                print("Button press detected. Spinning right motor 360 degrees.")
                double_motor.motor_run_for_degrees(360, motor=le.MOTOR_RIGHT, speed=30)

            last_button_state = latest_button_value

        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nCtrl+C received. Stopping tests.")
    if CONNECT_DOUBLE_MOTOR:
        double_motor.movement_stop()
finally:
    arduino_serial.close()


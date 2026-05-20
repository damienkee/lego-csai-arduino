"""Simple LEGO CSAI hardware test runner.

Set the boolean flags below to choose which devices to connect.
The script connects only the selected hardware and runs the matching test.
"""

import time

import legoeducation as le
import serial


CARD_COLOUR = le.LEGO_COLOR_RED
CARD_SERIAL = '0943'
TEST_DURATION_SECONDS = 5
SERIAL_PORT = 'COM7'
SERIAL_BAUDRATE = 9600
SERIAL_TIMEOUT_SECONDS = 1

# Change these booleans to match the hardware you want to test.
CONNECT_SINGLE_MOTOR = False
CONNECT_COLOR_SENSOR = False
CONNECT_DOUBLE_MOTOR = True
CONNECT_CONTROLLER = True


"""Connect to devices that are 'True' flags."""
print("Connecting to devices. Please wait...")

if CONNECT_SINGLE_MOTOR:
    single_motor = le.SingleMotor()
    single_motor.connect(card_color=CARD_COLOUR, card_serial=CARD_SERIAL)
    if not single_motor.connected:
        print('Error connecting to Single Motor.')
        exit(1) # error connecting
    print(f"Connected Single Motor")

if CONNECT_COLOR_SENSOR:
    colour_sensor = le.ColorSensor()
    colour_sensor.connect(card_color=CARD_COLOUR, card_serial=CARD_SERIAL)
    if not colour_sensor.connected:
        print('Error connecting to Colour Sensor.')
        exit(1) # error connecting
    print(f"Connected Colour Sensor")

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
    if CONNECT_SINGLE_MOTOR and not CONNECT_COLOR_SENSOR:
        """Move the single motor by 180 degrees."""
        print("Running single motor test: move 180 degrees.")
        single_motor.motor_run_for_degrees(180)
        print("Single motor test complete.")

    if CONNECT_SINGLE_MOTOR and CONNECT_COLOR_SENSOR:
        """Use the color sensor to choose a motor speed."""
        print("Running color sensor test for five seconds: green=fast, red=slow.")

        for _ in range(TEST_DURATION_SECONDS * 10):
            detected_colour = colour_sensor.sensor.color

            if detected_colour == le.LEGO_COLOR_GREEN:
                single_motor.motor_run(speed=80)
            elif detected_colour == le.LEGO_COLOR_RED:
                single_motor.motor_run(speed=10)
            else:
                single_motor.motor_stop()

            time.sleep(0.1)

        single_motor.motor_stop()
        print("Colour sensor test complete.")

    if CONNECT_DOUBLE_MOTOR and CONNECT_CONTROLLER:
        """Use the handheld controller to drive the double motor."""
        print("Running controller test for ten seconds: levers drive tank movement.")

        for i in range(TEST_DURATION_SECONDS * 10):
            if arduino_serial.in_waiting > 0:
                incoming_message = arduino_serial.readline().decode("ascii", errors="ignore").strip()
                if incoming_message:
                    print(f"Arduino serial received: {incoming_message}")

                if "B1" in incoming_message.upper():
                    print("Received B1 from Arduino. Running 360 degree spin.")
                    double_motor.movement_move_for_degrees(360)
                    continue

            speed_left = controller.sensor.leftPercent
            speed_right = controller.sensor.rightPercent
            double_motor.movement_move_tank(
                speed_left=speed_left,
                speed_right=speed_right,
            )

            # Send as CSV: leftPercent,rightPercent\n
            arduino_serial.write(f"{speed_left},{speed_right}\n".encode("ascii"))
            """print(f"{speed_left},{speed_right}\n")"""
            time.sleep(0.1)

        print("Controller test complete.")
finally:
    arduino_serial.close()


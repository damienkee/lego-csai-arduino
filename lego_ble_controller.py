"""Simple LEGO CSAI hardware test runner.

Set the boolean flags below to choose which devices to connect.
The script connects only the selected hardware and runs the matching test.
"""

import time

import legoeducation as le


CARD_COLOR = le.LEGO_COLOR_AZURE
CARD_SERIAL = "3683"
TEST_DURATION_SECONDS = 5

# Change these booleans to match the hardware you want to test.
CONNECT_SINGLE_MOTOR = True
CONNECT_COLOR_SENSOR = False
CONNECT_DOUBLE_MOTOR = False
CONNECT_CONTROLLER = False


def create_selected_devices():
    """Create only the devices enabled by the boolean flags."""
    devices = {
        "single_motor": None,
        "color_sensor": None,
        "double_motor": None,
        "controller": None,
    }

    if CONNECT_SINGLE_MOTOR:
        devices["single_motor"] = le.SingleMotor()
    if CONNECT_COLOR_SENSOR:
        devices["color_sensor"] = le.ColorSensor()
    if CONNECT_DOUBLE_MOTOR:
        devices["double_motor"] = le.DoubleMotor()
    if CONNECT_CONTROLLER:
        devices["controller"] = le.Controller()

    return devices


def selected_device_list(devices):
    """Return a simple list of device names and device objects."""
    selected = []

    if devices["single_motor"] is not None:
        selected.append(("Single Motor", devices["single_motor"]))
    if devices["color_sensor"] is not None:
        selected.append(("Color Sensor", devices["color_sensor"]))
    if devices["double_motor"] is not None:
        selected.append(("Double Motor", devices["double_motor"]))
    if devices["controller"] is not None:
        selected.append(("Controller", devices["controller"]))

    return selected


def connect_selected_devices(devices):
    """Connect all selected devices."""
    for label, device in selected_device_list(devices):
        print(f"Connecting {label}...")
        device.connect(card_color=CARD_COLOR, card_serial=CARD_SERIAL)
        if not getattr(device, "connected", False):
            print(f"Error connecting to {label}.")
            return False
        print(f"Connected {label}.")

    return True


def disconnect_selected_devices(devices):
    """Disconnect all selected devices."""
    for label, device in selected_device_list(devices):
        try:
            if getattr(device, "connected", False):
                print(f"Disconnecting {label}...")
                device.disconnect()
        except Exception as error:
            print(f"Disconnect failed for {label}: {error}")


def run_single_motor_test(single_motor):
    """Move the single motor by 180 degrees."""
    print("Running single motor test: move 180 degrees.")
    single_motor.motor_run_for_degrees(180)
    print("Single motor test complete.")


def run_color_sensor_test(single_motor, color_sensor):
    """Use the color sensor to choose a motor speed."""
    print("Running color sensor test for five seconds: green=fast, red=slow.")

    for _ in range(TEST_DURATION_SECONDS * 10):
        detected_color = color_sensor.sensor.color

        if detected_color == le.LEGO_COLOR_GREEN:
            single_motor.motor_run(speed=80)
        elif detected_color == le.LEGO_COLOR_RED:
            single_motor.motor_run(speed=10)
        else:
            single_motor.motor_stop()

        time.sleep(0.1)

    single_motor.motor_stop()
    print("Color sensor test complete.")


def run_controller_test(double_motor, controller):
    """Use the handheld controller to drive the double motor."""
    print("Running controller test for five seconds: levers drive tank movement.")

    for _ in range(TEST_DURATION_SECONDS * 10):
        speed_left = controller.sensor.leftPercent
        speed_right = controller.sensor.rightPercent
        double_motor.movement_move_tank(
            speed_left=speed_left,
            speed_right=speed_right,
        )
        time.sleep(0.1)

    print("Controller test complete.")


def run_selected_tests(devices):
    """Run the test that matches the currently selected devices."""
    single_motor = devices["single_motor"]
    color_sensor = devices["color_sensor"]
    double_motor = devices["double_motor"]
    controller = devices["controller"]

    if single_motor is not None and color_sensor is None:
        run_single_motor_test(single_motor)

    if single_motor is not None and color_sensor is not None:
        run_color_sensor_test(single_motor, color_sensor)

    if double_motor is not None and controller is not None:
        run_controller_test(double_motor, controller)

    if not any((single_motor, color_sensor, double_motor, controller)):
        print("No devices selected. Set one or more booleans near the top of the file.")


def main():
    devices = create_selected_devices()

    if not connect_selected_devices(devices):
        disconnect_selected_devices(devices)
        return 1

    try:
        run_selected_tests(devices)
        return 0
    finally:
        disconnect_selected_devices(devices)


if __name__ == "__main__":
    raise SystemExit(main())

"""
LEGO Bluetooth Low Energy (BLE) Controller

This module communicates with LEGO Bluetooth devices and sends
commands to an Arduino via serial port.
"""

import asyncio
import serial
import logging
from typing import Optional
from bleak import BleakClient, BleakScanner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LEGOBLEController:
    """Controller for LEGO BLE devices with Arduino serial communication."""

    def __init__(self, serial_port: str = "COM3", baud_rate: int = 9600):
        """
        Initialize the LEGO BLE Controller.

        Args:
            serial_port: Serial port for Arduino communication (e.g., 'COM3' or '/dev/ttyUSB0')
            baud_rate: Baud rate for serial communication (default: 9600)
        """
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.arduino_connection: Optional[serial.Serial] = None
        self.ble_client: Optional[BleakClient] = None
        self.lego_device_address: Optional[str] = None

    def connect_arduino(self) -> bool:
        """
        Connect to the Arduino via serial port.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.arduino_connection = serial.Serial(
                port=self.serial_port,
                baudrate=self.baud_rate,
                timeout=1
            )
            logger.info(f"Connected to Arduino on {self.serial_port}")
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to connect to Arduino: {e}")
            return False

    def disconnect_arduino(self) -> None:
        """Disconnect from the Arduino."""
        if self.arduino_connection and self.arduino_connection.is_open:
            self.arduino_connection.close()
            logger.info("Disconnected from Arduino")

    async def scan_lego_devices(self, timeout: float = 5.0) -> list[str]:
        """
        Scan for available LEGO Bluetooth devices.

        Args:
            timeout: Scan timeout in seconds

        Returns:
            List of discovered LEGO device addresses
        """
        logger.info(f"Scanning for LEGO devices (timeout: {timeout}s)")
        devices = []
        scanner = BleakScanner()
        discovered = await scanner.discover(timeout=timeout)

        for device in discovered:
            if device.name and "LEGO" in device.name.upper():
                devices.append(device.address)
                logger.info(f"Found LEGO device: {device.name} ({device.address})")

        return devices

    async def connect_lego_device(self, device_address: str) -> bool:
        """
        Connect to a LEGO BLE device.

        Args:
            device_address: Bluetooth address of the LEGO device

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.ble_client = BleakClient(device_address)
            await self.ble_client.connect()
            self.lego_device_address = device_address
            logger.info(f"Connected to LEGO device: {device_address}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to LEGO device: {e}")
            return False

    async def disconnect_lego_device(self) -> None:
        """Disconnect from the LEGO BLE device."""
        if self.ble_client and self.ble_client.is_connected:
            await self.ble_client.disconnect()
            logger.info("Disconnected from LEGO device")

    def send_to_arduino(self, command: str) -> bool:
        """
        Send a command to the Arduino via serial.

        Args:
            command: Command string to send to Arduino

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.arduino_connection or not self.arduino_connection.is_open:
            logger.error("Arduino not connected")
            return False

        try:
            self.arduino_connection.write(command.encode() + b'\n')
            logger.info(f"Sent to Arduino: {command}")
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to send to Arduino: {e}")
            return False

    def read_from_arduino(self, timeout: float = 1.0) -> Optional[str]:
        """
        Read a response from the Arduino via serial.

        Args:
            timeout: Read timeout in seconds

        Returns:
            Response string or None if no data received
        """
        if not self.arduino_connection or not self.arduino_connection.is_open:
            return None

        try:
            if self.arduino_connection.in_waiting > 0:
                response = self.arduino_connection.readline().decode().strip()
                logger.info(f"Received from Arduino: {response}")
                return response
        except serial.SerialException as e:
            logger.error(f"Failed to read from Arduino: {e}")

        return None

    async def run(self, device_address: Optional[str] = None) -> None:
        """
        Main run loop for the controller.

        Args:
            device_address: Optional LEGO device address. If not provided, scans for devices.
        """
        # Connect to Arduino
        if not self.connect_arduino():
            return

        try:
            # Connect to LEGO device
            if not device_address:
                devices = await self.scan_lego_devices()
                if not devices:
                    logger.error("No LEGO devices found")
                    return
                device_address = devices[0]

            if not await self.connect_lego_device(device_address):
                return

            logger.info("System ready. Type commands (or 'quit' to exit)")
            
            # Main command loop
            while True:
                try:
                    # In a real application, you would read from LEGO device here
                    # and forward data to Arduino as needed
                    await asyncio.sleep(0.1)

                except KeyboardInterrupt:
                    break

        finally:
            await self.disconnect_lego_device()
            self.disconnect_arduino()
            logger.info("Shutdown complete")


async def main():
    """Main entry point."""
    controller = LEGOBLEController(serial_port="COM3")
    await controller.run()


if __name__ == "__main__":
    asyncio.run(main())

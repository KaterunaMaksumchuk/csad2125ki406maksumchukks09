import serial
import serial.tools.list_ports

class SerialManager:
    def __init__(self):
        self.connection = None

    def get_available_ports(self):
        """Get list of available serial ports."""
        return [port.device for port in serial.tools.list_ports.comports()]

    def connect(self, port, baud_rate):
        """Establish serial connection."""
        try:
            self.connection = serial.Serial(port, baud_rate, timeout=1)
            return True
        except Exception as e:
            self.connection = None
            raise e

    def disconnect(self):
        """Close serial connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def is_connected(self):
        """Check if serial connection is active."""
        if self.connection:
            try:
                self.connection.write(b"\n")
                return True
            except:
                self.connection = None
        return False

    def send_command(self, command):
        """Send command through serial connection."""
        if self.connection:
            try:
                self.connection.write(f"{command}\n".encode())
                return True
            except:
                self.connection = None
                raise ConnectionError("Lost connection to device")
        return False

    def read_response(self):
        """Read response from serial connection."""
        if self.connection:
            try:
                return self.connection.readline().decode().strip()
            except:
                self.connection = None
                raise ConnectionError("Lost connection to device")
        return None
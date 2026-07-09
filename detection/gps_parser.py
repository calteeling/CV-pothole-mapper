import pynmea2
import serial
import threading
from datetime import datetime


class GPSParser:
    def __init__(self, port: str = "/dev/ttyACM0", baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self.current_lat = None
        self.current_lon = None
        self.current_speed = None
        self.timestamp = None
        self._running = False
        self._thread = None

    def _parse_sentence(self, sentence: str):
        try:
            msg = pynmea2.parse(sentence)
            if hasattr(msg, 'latitude') and hasattr(msg, 'longitude'):
                if msg.latitude and msg.longitude:
                    self.current_lat = msg.latitude
                    self.current_lon = msg.longitude
                    self.timestamp = datetime.utcnow()
            if hasattr(msg, 'spd_over_grnd') and msg.spd_over_grnd:
                self.current_speed = float(msg.spd_over_grnd) * 1.15078
        except pynmea2.ParseError:
            pass

    def _read_loop(self):
        with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
            while self._running:
                try:
                    line = ser.readline().decode('ascii', errors='replace').strip()
                    if line.startswith('$'):
                        self._parse_sentence(line)
                except Exception:
                    pass

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def get_coordinates(self):
        return self.current_lat, self.current_lon

    def get_speed_mph(self):
        return self.current_speed

    def has_fix(self):
        return self.current_lat is not None and self.current_lon is not None
import time
from detection.gps_parser import GPSParser

def test_gps_parser():
    print("Testing GPS parser on VK-162 dongle...")
    print("Make sure the GPS dongle is plugged into USB port")

    gps = GPSParser(port="/dev/ttyACM0", baudrate=9600)
    gps.start()

    print("Waiting for GPS fix (up to 60 seconds)...")
    timeout = 60
    elapsed = 0

    while not gps.has_fix() and elapsed < timeout:
        time.sleep(1)
        elapsed += 1
        if elapsed % 10 == 0:
            print(f"  Still waiting... {elapsed}s elapsed")

    if gps.has_fix():
        lat, lon = gps.get_coordinates()
        speed = gps.get_speed_mph()
        print(f"GPS fix acquired!")
        print(f"  Latitude: {lat}")
        print(f"  Longitude: {lon}")
        print(f"  Speed: {speed} mph")
    else:
        print("No GPS fix acquired within timeout")
        print("Check that dongle is plugged in and has clear sky view")

    gps.stop()


if __name__ == "__main__":
    test_gps_parser()
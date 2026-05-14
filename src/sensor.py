'''
Utility functions for reading sensor data

Adjusted code based on
https://randomnerdtutorials.com/raspberry-pi-bme280-python
'''

import smbus2
import bme280


# BME280 sensor address (default address)
ADDRESS = 0x76

# Initialize I2C bus
bus = smbus2.SMBus(1)

# Load calibration parameters
calibration_params = bme280.load_calibration_params(bus, ADDRESS)


def get_measure() -> bme280.compensated_readings:
    '''
    Get the current measurements from the BME280 sensor
    This includes temperature, humidity, and pressure.
    '''
    return bme280.sample(bus, ADDRESS, calibration_params)


if __name__ == "__main__":
    # example usage
    data = get_measure()
    print(data)

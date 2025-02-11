import time
import board
import adafruit_dht
from smbus2 
import SMBus  # For I2C communication with LCD
import RPi.GPIO as GPIO

# Initialize DHT11 sensor
dhtDevice = adafruit_dht.DHT11(board.D18)

# GPIO Pin Definitions
SMOKE_SENSOR_PIN = 17  # GPIO pin for FC-22 smoke sensor (via ADC module)
BUZZER_PIN = 27  # GPIO pin for buzzer
I2C_ADDRESS = 0x27  # I2C address for 16x2 LCD (commonly 0x27 or 0x3F)

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(SMOKE_SENSOR_PIN, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Initialize I2C LCD
bus = SMBus(1)

def lcd_write(cmd):
    bus.write_byte(I2C_ADDRESS, cmd)
    time.sleep(0.0001)

def lcd_display(line1, line2):
    # Clear LCD
    lcd_write(0x01)
    time.sleep(0.05)
    # Line 1
    lcd_write(0x80)
    for char in line1:
        bus.write_byte_data(I2C_ADDRESS, 0x40, ord(char))
    # Line 2
    lcd_write(0xC0)
    for char in line2:
        bus.write_byte_data(I2C_ADDRESS, 0x40, ord(char))

def check_thresholds(temp, humidity, smoke_detected):
    # Thresholds
    temp_threshold = 20
    smoke_threshold = 0  # Adjust based on smoke sensor calibration
    
    # Check thresholds and trigger actions
    if temp > temp_threshold or smoke_detected:
        lcd_display("ALERT!", f"T:{temp}C S:Smoke")
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
    else:
        lcd_display(f"T:{temp}C H:{humidity}%", "S:Normal")
        GPIO.output(BUZZER_PIN, GPIO.LOW)

try:
    while True:
        try:
            # Read DHT11 sensor
            temperature_c = dhtDevice.temperature
            humidity = dhtDevice.humidity
            
            # Read Smoke Sensor
            smoke_detected = GPIO.input(SMOKE_SENSOR_PIN)  # Replace with ADC value for analog
            
            # Print values (optional for debugging)
            print(f"Temp: {temperature_c}C, Humidity: {humidity}%, Smoke: {'Yes' if smoke_detected else 'No'}")
            
            # Check thresholds and update LCD/Buzzer
            check_thresholds(temperature_c, humidity, smoke_detected)

        except RuntimeError as error:
            print(f"DHT Error: {error.args[0]}")
            time.sleep(2.0)
            continue
        except Exception as error:
            dhtDevice.exit()
            GPIO.cleanup()
            raise error

        time.sleep(2.0)

except KeyboardInterrupt:
    print("Exiting program.")
    dhtDevice.exit()
    GPIO.cleanup()

#!/usr/bin/python3
import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_i2c_setup():
    try:
        # Check if i2c-tools is installed
        i2cdetect_output = subprocess.check_output(['i2cdetect', '-y', '1'], 
                                                 stderr=subprocess.STDOUT).decode()
        logger.info("I2C Bus Scan Results:")
        logger.info(i2cdetect_output)
        
        # Check for typical touch controller addresses (0x14 or 0x5d)
        if "14" in i2cdetect_output or "5d" in i2cdetect_output:
            logger.info("Touch controller detected!")
            return True
        else:
            logger.warning("No touch controller detected at expected addresses")
            return False
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running i2cdetect: {e}")
        logger.info("Please ensure i2c-tools is installed: sudo apt-get install i2c-tools")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def check_input_devices():
    try:
        xinput_output = subprocess.check_output(['xinput', 'list'], 
                                              stderr=subprocess.STDOUT).decode()
        logger.info("\nXInput Devices:")
        logger.info(xinput_output)
        
        if "WaveShare" in xinput_output:
            logger.info("Waveshare touch device found in xinput!")
            return True
        else:
            logger.warning("Waveshare touch device not found in xinput list")
            return False
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running xinput: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting touch screen diagnostics...")
    
    i2c_status = check_i2c_setup()
    input_status = check_input_devices()
    
    if i2c_status and input_status:
        logger.info("\nTouch screen appears to be properly configured!")
        sys.exit(0)
    else:
        logger.warning("\nSome issues detected with touch screen configuration")
        logger.info("Please ensure:")
        logger.info("1. I2C is enabled in raspi-config")
        logger.info("2. The correct dtoverlay is set in /boot/config.txt")
        logger.info("3. The touch screen is properly connected to the I2C pins")
        sys.exit(1)

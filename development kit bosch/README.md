# Bosch BME68x ESP32 DevKit Firmware

## Quick Start – Extract sensor data to SD card

1. **Download** this firmware package from the official Bosch website.

2. **Prepare the hardware**:
   - Insert a formatted SD card into the ESP32 DevKit board.
   - Connect the board to your PC via USB.

3. **Flash the firmware** (Windows):
   - Right-click on `Flash.bat` and select **Run as Administrator**.
   - Wait for the flashing process to complete (the ESP32 will reboot automatically).

4. **Collect data**:
   - After flashing, the sensor will start logging data directly to the SD card.
   - To stop, simply power off the board and remove the SD card.

5. **Retrieve your dataset**:
   - Insert the SD card into your PC.
   - Copy the `.csv` or `.txt` log files – these contain your sensor data (IAQ, pressure, temperature, humidity).

> **Note**: If `Flash.bat` fails, install the latest CP210x USB-to-UART driver and verify the COM port in Device Manager.
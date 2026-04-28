#ifndef COMM_MUX_H
#define COMM_MUX_H

#include "Arduino.h"
#include "Wire.h"
#include "SPI.h"

/**
 * Datatype working as an interface descriptor
 */
typedef struct {
   TwoWire *wireobj;
   SPIClass *spiobj;
   uint8_t select;
} commMux;

/**
 * @brief Function to configure the communication across sensors
 * @param wireobj : The TwoWire object
 * @param spiobj  : The SPIClass object
 * @param idx     : Selected sensor for communication interface
 * @param comm    : Structure for selected sensor
 * @return        : Structure holding the communication setup
 */
commMux commMuxSetConfig(TwoWire &wireobj, SPIClass &spiobj, uint8_t idx, commMux &comm);

/**
 * @brief Function to trigger the communication
 * @param wireobj : The TwoWire object
 * @param spiobj  : The SPIClass object
 */
void commMuxBegin(TwoWire &wireobj, SPIClass &spiobj);

/**
 * @brief Function to write the sensor data to the register
 * @param reg_addr : Address of the register
 * @param reg_data : Pointer to the data to be written
 * @param length   : length of the register data
 * @param intf_ptr : Pointer to the interface descriptor
 * @return 0 if successful, non-zero otherwise
 */
int8_t commMuxWrite(uint8_t reg_addr, const uint8_t *reg_data, uint32_t length, void *intf_ptr);

/**
 * @brief Function to read the sensor data from the register
 * @param reg_addr : Address of the register
 * @param reg_data : Pointer to the data to be read from the sensor
 * @param length   : length of the register data
 * @param intf_ptr : Pointer to the interface descriptor
 * @return 0 if successful, non-zero otherwise
 */
int8_t commMuxRead(uint8_t reg_addr, uint8_t *reg_data, uint32_t length, void *intf_ptr);

/**
 * @brief Function to maintain a delay between communication
 * @param period_us   : Time delay in micro secs
 * @param intf_ptr    : Pointer to the interface descriptor
 */
void commMuxDelay(uint32_t period_us, void *intf_ptr);

#endif /* COMM_MUX_H */
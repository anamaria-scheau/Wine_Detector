/**
 * BSEC Configuration for Wine Detection
 * This file defines which virtual sensors to enable.
 * The trained models are loaded separately from subfolders.
 */

#ifndef BSEC_CONFIG_H
#define BSEC_CONFIG_H

#include <bsec2.h>
#include "presence_model/bsec_selectivity.h"

// Sample rate configuration
#define SAMPLE_RATE BSEC_SAMPLE_RATE_LP  // Low power mode (3 second intervals)

// Virtual sensors to enable (these are always active regardless of which model we load)
static const bsec_virtual_sensor_t SENSOR_LIST[] = {
    BSEC_OUTPUT_SENSOR_HEAT_COMPENSATED_TEMPERATURE,
    BSEC_OUTPUT_SENSOR_HEAT_COMPENSATED_HUMIDITY,
    BSEC_OUTPUT_RAW_PRESSURE,
    BSEC_OUTPUT_RAW_GAS,
    BSEC_OUTPUT_IAQ,
    BSEC_OUTPUT_GAS_ESTIMATE_1,   // For model predictions
    BSEC_OUTPUT_GAS_ESTIMATE_2,   // For model predictions
    BSEC_OUTPUT_GAS_ESTIMATE_3,   // For model predictions
    BSEC_OUTPUT_GAS_ESTIMATE_4    // For model predictions
};

#define NUM_SENSORS (sizeof(SENSOR_LIST) / sizeof(SENSOR_LIST[0]))

#endif // BSEC_CONFIG_H







// /**
//  * BSEC Configuration for Wine Detection
//  * Optimized for volatile organic compound detection
//  * 
//  * This is a user-defined configuration file that specifies 
//  * which virtual sensors should be enabled and at what sampling 
//  * rate the BSEC algorithm should 
//   operate.
//  * 
//  */

// #ifndef BSEC_CONFIG_H
// #define BSEC_CONFIG_H

// #include <bsec2.h>
// #include "bsec_selectivity.h"

// // Sample rate configuration
// #define SAMPLE_RATE BSEC_SAMPLE_RATE_LP  // Low power mode (3 second intervals)

// // Virtual sensors to enable
// static const bsec_virtual_sensor_t SENSOR_LIST[] = {
//     BSEC_OUTPUT_SENSOR_HEAT_COMPENSATED_TEMPERATURE,
//     BSEC_OUTPUT_SENSOR_HEAT_COMPENSATED_HUMIDITY,
//     BSEC_OUTPUT_RAW_PRESSURE,
//     BSEC_OUTPUT_RAW_GAS,
//     BSEC_OUTPUT_IAQ,
//     BSEC_OUTPUT_STABILIZATION_STATUS,
//     BSEC_OUTPUT_RUN_IN_STATUS
// };

// #define NUM_SENSORS (sizeof(SENSOR_LIST) / sizeof(SENSOR_LIST[0]))

// #endif // BSEC_CONFIG_H
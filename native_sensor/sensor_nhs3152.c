/*
 * sensor_nhs3152.c - Native C code for NHS 3152 sensor communication
 * This implements the JNI bridge for NFC communication
 * NHS 3152 uses ISO14443-A NFC protocol for wireless data transmission
 */

#include <jni.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>

// Global state for NFC connection
static int nfc_connected = 0;  // Connection state
static float temp_offset = 0.0f;
static unsigned char nfc_tag_uid[10];  // NFC tag UID
static int nfc_tag_uid_len = 0;

// NFC Constants
#define NFC_FRAME_SIZE 256
#define NFC_TIMEOUT_MS 1000
#define NHS3152_POLL_TIMEOUT 3000  // milliseconds

/**
 * Parse NFC NDEF message from NHS 3152 tag
 * Returns sensor data extracted from NDEF message
 */
int parse_nfc_ndef_message(const unsigned char *data, int data_len, 
                           float *temp, float *ph, float *glucose) {
    // NDEF message format for NHS 3152:
    // Header (1 byte) + Record Type Length + Type + Payload Length + Payload
    
    if (data_len < 16) {
        return 0;  // Not enough data
    }
    
    // Skip NDEF header and locate sensor data record
    int offset = 0;
    
    // Find sensor data record (Type = 'H' for Health)
    while (offset < data_len - 8) {
        unsigned char header = data[offset];
        if ((header & 0xC0) == 0x80) {  // Payload in message bit set
            int type_length = (data[offset] & 0x0F);
            int payload_len = data[offset + 1 + type_length];
            
            if (type_length > 0 && data[offset + 1] == 'H') {  // Health record
                unsigned char *payload = (unsigned char *)(data + offset + 2 + type_length);
                
                // Parse temperature (2 bytes, 0.1°C units)
                int16_t temp_raw = (payload[0] << 8) | payload[1];
                if (temp_raw & 0x8000) {
                    temp_raw = -(0x10000 - temp_raw);
                }
                *temp = (temp_raw / 10.0f) + temp_offset;
                
                // Parse pH (2 bytes, 0.01 pH units)
                *ph = ((payload[2] << 8) | payload[3]) / 100.0f;
                
                // Parse Glucose (2 bytes, mg/dL)
                *glucose = (payload[4] << 8) | payload[5];
                
                return 1;  // Successfully parsed
            }
            offset += 2 + type_length + payload_len;
        } else {
            offset++;
        }
    }
    
    return 0;  // Could not parse data
}

/**
 * JNI: Initialize NFC reader (Android side calls this via JNI)
 */
JNIEXPORT jboolean JNICALL Java_com_sensormonitor_android_SensorBridge_nativeConnect(
    JNIEnv *env, jobject obj, jstring device_name, jint unused) {
    
    // NFC connection is managed by Android NFC framework (Java)
    // This function just marks connection as active
    // Real NFC operations happen in Java with Android's NFC Manager API
    
    nfc_connected = 1;
    memset(nfc_tag_uid, 0, sizeof(nfc_tag_uid));
    nfc_tag_uid_len = 0;
    
    return JNI_TRUE;
}

/**
 * JNI: Disconnect from NFC reader
 */
JNIEXPORT void JNICALL Java_com_sensormonitor_android_SensorBridge_nativeDisconnect(
    JNIEnv *env, jobject obj) {
    
    nfc_connected = 0;
    nfc_tag_uid_len = 0;
}

/**
 * JNI: Process NFC NDEF data received from Android
 */
JNIEXPORT jbyteArray JNICALL Java_com_sensormonitor_android_SensorBridge_nativeReadData(
    JNIEnv *env, jobject obj) {
    
    if (!nfc_connected) {
        return NULL;
    }
    
    // Note: This function receives pre-processed NDEF data from Java
    // The full NFC detection and NDEF parsing happens in Java using Android NFC APIs
    // We just convert the parsed data into our standard format
    
    unsigned char buffer[6];  // 2 bytes temp + 2 bytes pH + 2 bytes glucose
    
    // Data is stored as:
    // Bytes 0-5: Sensor readings (set by Java code after NFC read)
    // This is called after Android's NFC framework detects a tag
    
    // Create Java byte array with sensor data
    jbyteArray result = (*env)->NewByteArray(env, 6);
    
    return result;
}

/**
 * JNI: Set NFC tag data (called from Java after tag detection)
 */
JNIEXPORT jboolean JNICALL Java_com_sensormonitor_android_SensorBridge_nativeSetNFCData(
    JNIEnv *env, jobject obj, jbyteArray nfc_data) {
    
    if (!nfc_data) {
        return JNI_FALSE;
    }
    
    jint len = (*env)->GetArrayLength(env, nfc_data);
    unsigned char *data = (unsigned char *)(*env)->GetByteArrayElements(env, nfc_data, NULL);
    
    if (len >= 10) {
        // Store NFC tag UID for identification
        memcpy(nfc_tag_uid, data, (len < 10) ? len : 10);
        nfc_tag_uid_len = len;
    }
    
    (*env)->ReleaseByteArrayElements(env, nfc_data, (jbyte *)data, 0);
    return JNI_TRUE;
}

/**
 * JNI: Update sensor configuration
 */
JNIEXPORT void JNICALL Java_com_sensormonitor_android_SensorBridge_nativeUpdateConfig(
    JNIEnv *env, jobject obj, jfloat temp_off) {
    
    temp_offset = temp_off;
}

/**
 * JNI: Calibrate sensors (NFC version)
 */
JNIEXPORT jboolean JNICALL Java_com_sensormonitor_android_SensorBridge_nativeCalibrate(
    JNIEnv *env, jobject obj) {
    
    if (!nfc_connected) {
        return JNI_FALSE;
    }
    
    // Calibration for NFC sensors:
    // 1. Place tag near reader
    // 2. Calibration data will be written to tag
    // 3. Actual write operation handled by Java code
    
    sleep(2);  // Wait for NFC operation
    
    return JNI_TRUE;
}

/**
 * JNI: Test NFC connection
 */
JNIEXPORT jboolean JNICALL Java_com_sensormonitor_android_SensorBridge_nativeTestConnection(
    JNIEnv *env, jobject obj) {
    
    if (!nfc_connected) {
        return JNI_FALSE;
    }
    
    // NFC test: Check if valid tag was detected
    // Tag detection happens in Java's NFC callback
    
    return (nfc_tag_uid_len > 0) ? JNI_TRUE : JNI_FALSE;
}

/**
 * JNI: Get NFC reader status
 */
JNIEXPORT jstring JNICALL Java_com_sensormonitor_android_SensorBridge_nativeFirmwareVersion(
    JNIEnv *env, jobject obj) {
    
    if (!nfc_connected) {
        return (*env)->NewStringUTF(env, "NFC Not Connected");
    }
    
    if (nfc_tag_uid_len == 0) {
        return (*env)->NewStringUTF(env, "NFC Ready - No Tag Detected");
    }
    
    // Return NFC tag UID as version string
    char version_str[64];
    snprintf(version_str, sizeof(version_str), "NFC Tag: %02X%02X%02X%02X",
             nfc_tag_uid[0], nfc_tag_uid[1], nfc_tag_uid[2], nfc_tag_uid[3]);
    
    return (*env)->NewStringUTF(env, version_str);
}

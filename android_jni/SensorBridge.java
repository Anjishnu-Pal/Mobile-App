/*
 * SensorBridge.java - JNI interface for NHS 3152 sensor communication via NFC
 * This class bridges Python (Kivy) with native C/C++ code for NFC communication
 */

package com.sensormonitor.android;

import android.app.Activity;
import android.content.Context;
import android.nfc.NfcAdapter;
import android.nfc.Tag;
import android.nfc.tech.Ndef;
import android.nfc.tech.NdefFormatable;
import android.nfc.NdefMessage;
import android.nfc.NdefRecord;
import android.os.Bundle;
import android.util.Log;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class SensorBridge implements NfcAdapter.ReaderCallback {
    
    static {
        // Load native library
        System.loadLibrary("sensor_nhs3152");
    }
    
    private NfcAdapter nfcAdapter;
    private Context context;
    private Activity activity;
    private boolean connected = false;
    private boolean isReading = false;
    private Tag currentTag = null;
    private float[] lastSensorData = null;
    
    private static final String TAG = "SensorBridge";
    
    // NFC constants
    private static final int NFC_READER_MODE = NfcAdapter.FLAG_READER_NFC_A | 
                                                NfcAdapter.FLAG_READER_NFC_B |
                                                NfcAdapter.FLAG_READER_SKIP_NDEF_CHECK;
    
    public SensorBridge() {
        // Constructor
    }
    
    public SensorBridge(Context context) {
        this.context = context;
        this.nfcAdapter = NfcAdapter.getDefaultAdapter(context);
    }
    
    public SensorBridge(Activity activity) {
        this.activity = activity;
        this.context = activity.getApplicationContext();
        this.nfcAdapter = NfcAdapter.getDefaultAdapter(context);
    }
    
    /**
     * Connect to NFC reader
     */
    public boolean connect(Map<String, Object> config) {
        try {
            if (nfcAdapter == null) {
                Log.e(TAG, "NFC not supported on this device");
                return false;
            }
            
            if (!nfcAdapter.isEnabled()) {
                Log.e(TAG, "NFC is not enabled");
                return false;
            }
            
            connected = nativeConnect("NFC Mode", 0);
            
            // Start NFC reader mode
            if (connected && activity != null) {
                enableReaderMode();
            }
            
            return connected;
        } catch (Exception e) {
            Log.e(TAG, "Error connecting to NFC: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Enable NFC reader mode
     */
    private void enableReaderMode() {
        if (nfcAdapter != null && activity != null) {
            Bundle options = new Bundle();
            options.putInt(NfcAdapter.EXTRA_READER_PRESENCE_CHECK_DELAY, 250);
            
            nfcAdapter.enableReaderMode(activity, this, NFC_READER_MODE, options);
            isReading = true;
            Log.i(TAG, "NFC reader mode enabled");
        }
    }
    
    /**
     * Disable NFC reader mode
     */
    private void disableReaderMode() {
        if (nfcAdapter != null && activity != null) {
            nfcAdapter.disableReaderMode(activity);
            isReading = false;
            Log.i(TAG, "NFC reader mode disabled");
        }
    }
    
    /**
     * Disconnect from NFC reader
     */
    public void disconnect() {
        if (connected) {
            disableReaderMode();
            nativeDisconnect();
            connected = false;
        }
    }
    
    /**
     * Read parsed sensor data
     */
    public byte[] readRawData() {
        if (!connected) {
            return null;
        }
        return nativeReadData();
    }
    
    /**
     * Get last sensor reading
     */
    public float[] getSensorReading() {
        return lastSensorData;
    }
    
    /**
     * Update sensor configuration
     */
    public boolean updateConfig(Map<String, Object> config) {
        try {
            Float tempOffset = ((Number) config.get("temp_offset")).floatValue();
            nativeUpdateConfig(tempOffset);
            return true;
        } catch (Exception e) {
            Log.e(TAG, "Error updating config: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Calibrate sensors via NFC
     */
    public boolean calibrate() {
        if (!connected) {
            return false;
        }
        return nativeCalibrate();
    }
    
    /**
     * Test NFC connection
     */
    public boolean testConnection() {
        if (!connected) {
            return false;
        }
        return nativeTestConnection();
    }
    
    /**
     * Get NFC adapter status/firmware version
     */
    public String getFirmwareVersion() {
        if (!connected) {
            return "NFC Not Connected";
        }
        return nativeFirmwareVersion();
    }
    
    /**
     * Parse NDEF message from NHS 3152 tag
     */
    public float[] parseHealthData(byte[] data) {
        float[] sensorData = new float[3];  // temp, pH, glucose
        
        try {
            // NDEF payload format for NHS 3152 health tag:
            // Bytes 0-1: Temperature (signed, 0.1°C units)
            // Bytes 2-3: pH (0.01 units)
            // Bytes 4-5: Glucose (mg/dL)
            
            if (data.length >= 6) {
                // Temperature
                int tempRaw = ((data[0] & 0xFF) << 8) | (data[1] & 0xFF);
                if ((tempRaw & 0x8000) != 0) {
                    tempRaw = -(0x10000 - tempRaw);
                }
                sensorData[0] = tempRaw / 10.0f;  // Convert to °C
                
                // pH
                int phRaw = ((data[2] & 0xFF) << 8) | (data[3] & 0xFF);
                sensorData[1] = phRaw / 100.0f;
                
                // Glucose
                int glucoseRaw = ((data[4] & 0xFF) << 8) | (data[5] & 0xFF);
                sensorData[2] = glucoseRaw;
                
                lastSensorData = sensorData;
                return sensorData;
            }
        } catch (Exception e) {
            Log.e(TAG, "Error parsing health data: " + e.getMessage());
        }
        
        return null;
    }
    
    /**
     * NFC Reader Callback - called when NFC tag is detected
     */
    @Override
    public void onTagDiscovered(Tag tag) {
        currentTag = tag;
        Log.i(TAG, "NFC tag discovered");
        
        try {
            // Try to read NDEF message
            Ndef ndef = Ndef.get(tag);
            if (ndef != null) {
                ndef.connect();
                NdefMessage ndefMessage = ndef.getNdefMessage();
                
                if (ndefMessage != null) {
                    NdefRecord[] records = ndefMessage.getRecords();
                    
                    for (NdefRecord record : records) {
                        byte[] payload = record.getPayload();
                        
                        // Check for health record type
                        if (record.getTnf() == NdefRecord.TNF_WELL_KNOWN &&
                            record.getType()[0] == 'H') {  // Health record
                            
                            // Parse and store sensor data
                            float[] sensorData = parseHealthData(payload);
                            if (sensorData != null) {
                                Log.i(TAG, String.format(
                                    "Sensor Data - Temp: %.1f°C, pH: %.2f, Glucose: %.0f",
                                    sensorData[0], sensorData[1], sensorData[2]
                                ));
                            }
                            break;
                        }
                    }
                }
                ndef.close();
            }
        } catch (IOException e) {
            Log.e(TAG, "Error reading NFC tag: " + e.getMessage());
        }
    }
    
    /**
     * Write calibration data to NFC tag
     */
    public boolean writeCalibrationToTag(byte[] calibrationData) {
        if (currentTag == null) {
            Log.e(TAG, "No tag available for writing");
            return false;
        }
        
        try {
            Ndef ndef = Ndef.get(currentTag);
            if (ndef != null) {
                ndef.connect();
                
                // Create NDEF record with calibration data
                NdefRecord calibRecord = new NdefRecord(
                    NdefRecord.TNF_WELL_KNOWN,
                    new byte[]{'C'},  // Calibration record
                    new byte[]{},
                    calibrationData
                );
                
                NdefMessage ndefMessage = new NdefMessage(
                    new NdefRecord[]{calibRecord}
                );
                
                ndef.writeNdefMessage(ndefMessage);
                ndef.close();
                
                Log.i(TAG, "Calibration data written to tag");
                return true;
            }
        } catch (IOException e) {
            Log.e(TAG, "Error writing to tag: " + e.getMessage());
        }
        
        return false;
    }
    
    // Native method declarations
    private native boolean nativeConnect(String deviceName, int unused);
    private native void nativeDisconnect();
    private native byte[] nativeReadData();
    private native void nativeUpdateConfig(float tempOffset);
    private native boolean nativeCalibrate();
    private native boolean nativeTestConnection();
    private native String nativeFirmwareVersion();
    private native boolean nativeSetNFCData(byte[] nfcData);
}

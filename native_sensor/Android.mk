# Android NDK build file for NHS 3152 sensor library

LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE := sensor_nhs3152

LOCAL_SRC_FILES := sensor_nhs3152.c

LOCAL_CFLAGS := -Wall -O2

include $(BUILD_SHARED_LIBRARY)

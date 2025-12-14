# Smart Safety Bracelet for Emergency Assistance

## Overview
The Smart Safety Bracelet is a wearable emergency device designed to help users
send SOS alerts along with real-time GPS location data. The system is built using
ESP32-based microcontrollers and LoRa communication, allowing it to function
without SIM cards or mobile data.

## Problem Statement
In emergency situations, especially in areas with poor mobile network coverage,
traditional smartphone-based safety solutions may fail. This project aims to
provide a reliable, low-power, and independent safety system for emergency alerting.

## System Architecture
The project consists of two embedded units:

### 1. Sender Unit (ESP32-C3 – Bracelet)
- Worn by the user as a safety bracelet
- Reads GPS location data
- Sends SOS and location information via LoRa
- Triggered by an emergency button press
- Provides vibration feedback to the user

### 2. Receiver Unit (ESP32 – Gateway)
- Acts as a local gateway/receiver
- Receives SOS and GPS data from the bracelet via LoRa
- Processes incoming messages
- Can be extended to trigger alarms, logging, or notifications

## Technologies Used
- ESP32-C3 (Sender)
- ESP32 (Receiver)
- GPS Module (Neo-6)
- LoRa Module (SX1278)
- MicroPython
- Python

## Key Features
- SOS emergency alert system
- Real-time GPS location transmission
- Long-range LoRa communication
- Modular multi-file firmware design
- Low-power wearable-friendly approach

## Project Status
Prototype completed and tested.

## Future Improvements
- Hardware miniaturization for wearable use
- Improved power management and battery optimization
- Encrypted LoRa communication
- Integration with multiple receiver nodes

## System Diagram
![System Architecture](docs/ESP32C3(2).png)

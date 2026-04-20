# ⚡ Dynamic Line Rating (DLR) System for Alberta Transmission Networks

## 📘 Overview
This project presents a **laboratory-scale Dynamic Line Rating (DLR) system** developed as part of **ENEL 678 – Graduate Project in Electrical Engineering** at the University of Calgary.

The system computes real-time transmission line ampacity using environmental data and directly integrates with **PSSE** to dynamically update line thermal limits, improving **grid utilization, reliability, and renewable energy integration**.


## 🎯 Objectives
- Develop a **real-time environmental sensing system**
- Implement **IEEE 738 thermal model** for ampacity calculation
- Integrate DLR results into **PSSE for real-time simulation**
- Perform **N-1 contingency analysis**
- Validate system performance using hardware-in-the-loop testing


## ⚙️ System Architecture

### 🔌 Hardware
- Arduino UNO / ESP32 (data acquisition)
- Temperature sensor (TMP36)
- Anemometer (wind speed)
- Light sensor (solar irradiance)

### 💻 Software
- Python (DLR computation + PSSE interface)
- PSSE (power system simulation)
- Excel (data logging & validation)


## 🔄 Data Flow

- Environmental data is collected via Arduino
- Python processes the data using IEEE 738 equations
- Computed ampacity is converted and sent to PSSE
- PSSE updates transmission line ratings in real time

## 🔍 Methodology

### 1. Data Acquisition
- Real-time sensing of:
  - Temperature
  - Wind speed
  - Solar irradiance  
- Sampling rate: **1 Hz**

### 2. DLR Computation
- Implemented **IEEE 738 heat balance model**
- Calculates conductor ampacity dynamically based on environmental conditions

### 3. PSSE Integration
- Python script updates **line thermal limits (RATEA/B/C)**
- Enables real-time system response analysis

### 4. Validation
- Sensor accuracy validation (±0.5 °C, ±0.5 m/s)
- Benchmark comparison (≤10% deviation)
- Hardware-in-the-loop testing
- Continuous system monitoring


## 📊 Key Results
- 🔻 **15–17% reduction in line loading**
- ⚡ Increased **thermal headroom**
- 📉 Bus voltage deviation within **1%**
- ⏱️ **≥95% system uptime**
- 📡 <1% data loss during operation


## 🧪 Features
- Real-time DLR computation (1-second updates)
- Direct **Python–PSSE integration**
- Automated transmission line rating updates
- N-1 contingency analysis capability
- Hardware-in-the-loop validation


## ⚠️ Limitations
- Laboratory-scale prototype
- Limited to selected **138 kV transmission lines**
- Sensor accuracy impacts final results
- Not deployed on live grid infrastructure

## 🚀 Conclusion
This project demonstrates a practical and cost-effective approach to implementing **Dynamic Line Rating (DLR)** using real-time environmental data and direct simulation integration. The system shows strong potential for improving transmission efficiency and enabling higher penetration of renewable energy in modern power systems.

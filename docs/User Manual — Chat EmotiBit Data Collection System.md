# User Manual — Chat EmotiBit Data Collection System

## Version  
2026-03-XX

## Overview

Welcome to the **User Manual** for the Chat EmotiBit Data Collection System.  
This guide is designed for **operators, students, and lab personnel** who will set up experiments, collect multimodal physiological data, and use the system to analyze stress-related signals.  
The manual is written with **progressive disclosure**, so you learn *what the system does, why it matters, and how to do it correctly*.

This manual uses **illustrated placeholders** that you can later populate with your own figures.

---

# Table of Contents

1. Introduction  
2. System Components  
3. Getting Started  
   - Lab Setup Wizard  
   - Subject Setup Wizard  
4. Running an Experiment  
5. Interpreting Results  
6. Troubleshooting  
7. Best Practices  
8. Glossary of Terms  
9. Appendix  
   - Signal Visualizations  
   - Synchronization Examples

---

## 1. Introduction

This system enables recording and analysis of physiological signals — including **heart rate variability (HRV)**, **electrodermal activity (EDA)**, and motion — captured from:

- **EmotiBit sensors**
- **Polar heart rate devices**
- Optional audio event markers

The goal is to provide a **robust, self-validating workflow** with **guided assistance** so that experiments can be run reproducibly and data can be trusted.

---

## 2. System Components

### 2.1 Hardware

The system uses:

- **EmotiBit wearable sensor**
- **Polar HR monitor**
- **Audio marker source** (e.g., speaker)

Placeholders:

![Sensor Placement](figures/emotibit_polar_setup.png)  
*Figure 2-1: Example EmotiBit and Polar sensor placement on subject*

---

### 2.2 Software

- **Frontend Web App (Electron / Browser)**  
  For wizards, guided setup, and dashboards.

- **Backend API (Python)**  
  For parsing, synchronization, cleaning, features, and scoring.

- **AI Assist Module**  
  Provides explanations and diagnostics (via text & images).

- **Kubios Integration**  
  Uses either scripted automation or manual export for HRV analysis.

---

## 3. Getting Started

### 3.1 Lab Setup Wizard

Before running subjects, perform **Lab Setup**:

#### Step 1 — Device Detection

The system will detect connected EmotiBit or Polar devices.

Placeholder:

![Device Detection](figures/lab_wizard_device_detect.png)  
*Figure 3-1: Lab wizard detecting hardware*

#### Step 2 — Clock Synchronization

To align time across devices:

- Ensure both devices’ clocks are set consistently.
- Run a quick capture with event markers.

Placeholder:

![Clock Synchronization](figures/lab_wizard_clock_sync.png)  
*Figure 3-2: Lab clock sync interface*

---

#### Step 3 — Audio Marker Calibration

Audio markers are used to align streams.

Placeholder:

![Audio Markers](figures/lab_wizard_audio_markers.png)  
*Figure 3-3: Audio marker setup screen*

---

#### Step 4 — Save Lab Profile

After calibration, click **Save Settings**.  
Your lab profile stores:

- Clock offset model
- Preferred audio markers
- Calibration status

---

### 3.2 Subject Setup Wizard

Each session should start with **Subject Setup**.

#### Step 1 — Participant Information

Enter:

- Subject ID
- Session name
- Notes (optional)

---

#### Step 2 — EmotiBit Placement Check

Attach the EmotiBit sensor where recommended:

Placeholder:

![EmotiBit Placement](figures/emotibit_placement.png)  
*Figure 3-4: Correct EmotiBit placement example*

The system will evaluate sensor contact and signal quality.

---

#### Step 3 — Polar Strap Fit

Ensure the Polar strap is snug and detects beat intervals.

Placeholder:

![Polar Strap](figures/polar_strap_fit.png)  
*Figure 3-5: Polar strap fit example*

---

#### Step 4 — Marker Preview

Record and confirm at least **three event markers**:

- Start of session
- Midpoint
- End of session

The wizard previews marker times and quality.

---

## 4. Running an Experiment

### 4.1 Recording Data

After setup, begin recording:

- Press **Start Session**
- Perform experiment tasks
- Insert markers at condition changes

---

### 4.2 Uploading Data

After the session:

- Navigate to **Session Upload**
- Drag & drop or select files
  - EmotiBit log
  - Polar export
  - Marker log

The system auto-parses and begins processing.

---

## 5. Interpreting Results

### 5.1 Quality Score Panel

Each session yields a **Quality Score**:

Placeholder:

![Quality Score](figures/quality_score.png)  
*Figure 5-1: Quality score breakdown*

Score components include:

- Signal integrity
- Artifact levels
- Synchronization accuracy
- Marker coverage

---

### 5.2 HRV Results

The HRV panel shows:

- Time domain metrics (RMSSD, SDNN)
- Frequency domain
- Trend plots

Placeholder:

![HRV Results](figures/hrv_results.png)  
*Figure 5-2: HRV result visualization*

---

### 5.3 EDA Panel

Shows:

- Tonic level
- Phasic peak count
- EDA over time

Placeholder:

![EDA Panel](figures/eda_panel.png)  
*Figure 5-3: EDA feature display*

---

## 6. Troubleshooting

### 6.1 Low Signal Quality

Common causes:

- Poor sensor contact
- Excessive motion
- Loose Polar strap

Solutions:

- Re-position sensor
- Re-tighten strap
- Re-run pre-session check

---

### 6.2 Marker Mismatch

If markers fail to align:

Placeholder:

![Sync Error](figures/sync_error.png)  
*Figure 6-1: Sync error example*

Try:

- Replay marker tones louder
- Re-capture markers
- Check clock sync

---

## 7. Best Practices

- Sync clocks before experiments.
- Use distinct audio markers.
- Make sure subject is comfortable.
- Avoid excessive movement during measurement.

---

## 8. Glossary of Terms

- **Event Marker:** A time cue inserted to align streams.
- **HRV:** Heart rate variability, a stress measure.
- **EDA:** Electrodermal activity, linked to arousal.
- **Sync Model:** Mathematical mapping between device clocks.

---

## 9. Appendix

### 9.1 Signal Visualizations

Placeholder:

![Signal Overlay](figures/signal_overlay.png)  
*Figure App-1: Aligned waves of raw signal*

---

### 9.2 Synchronization Examples

Placeholder:

![Sync Timeline](figures/sync_timeline.png)  
*Figure App-2: Timeline of markers across devices*

---

*End of User Manual*
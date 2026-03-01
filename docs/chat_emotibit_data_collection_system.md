# Chat EmotiBit Data Collection System — Architecture Specification

## Version
2026-03-XX

## Purpose
This document defines the architecture, components, interfaces, data flows, and integration strategy for the Multimodal Stress Analysis Web System — a platform that ingests Polar ECG/RR and EmotiBit physiological signals, self-tests, synchronizes, extracts features (HRV/EDA/respiration), and produces interpretable stress metrics with AI assistance.

Includes:
- Hybrid user knowledge tracking (lab + session)  
- Kubios integration (primary & fallback)  
- AI assist (Text + Image)  
- Quality scoring framework  
- Wizard-driven UI flows

---

## 1. System Overview

**Goal:** End-to-end stress analysis with guided UI and self-healing workflows.

**Key data streams:**
- Polar ECG/RR intervals  
- EmotiBit: PPG, EDA, IMU, temperature  
- Event markers (audio)

**Core workflows:**
1. Lab setup and calibration  
2. Subject session setup and data collection  
3. Signal synchronization and cleaning  
4. Feature extraction  
5. Stress score computation  
6. Reporting + dashboards  
7. AI assistant (text + image)

---

## 2. High-Level Architecture

```
+----------------------------------------------------------+
|                 Frontend (Web / Electron)                |
|   - Wizards & Guided Flows                                |
|   - Dashboards & Reports                                  |
|   - Inline Help + AI Assistance Widgets                   |
+----------------------------|-----------------------------+
                             |
           REST / Websocket API | JSON + Images
                             |
+----------------------------v-----------------------------+
|                Backend API (FastAPI/Python)              |
|   Modules:                                               |
|    • Session Manager                                     |
|    • Parser (EmotiBit/Polar/Markers)                     |
|    • Synchronization & Drift Correction                  |
|    • Cleaning & Artifact Handling                        |
|    • Feature Extractors (HRV, EDA, Resp)                  |
|    • Stress Scorer                                        |
|    • Kubios Integration (Runner + Adapter)                |
|    • AI Assist Adapter (Gemini + switchable providers)    |
|    • User Knowledge Tracker (Lab + Session)               |
|    • Quality Scorer                                       |
|    • Reporting & Export                                   |
+----------------------------|-----------------------------+
                             |
                             v
+----------------------------+-----------------------------+
|                         PostgreSQL DB                    |
|  Tables:                                                  |
|   subjects, sessions, time_series_*, sync_models,         |
|   hrv_results, eda_features, stress_scores, quality_scores,
|   user_profiles, lab_profile                              |
+----------------------------------------------------------+
```

---

## 3. Technology Stack

| Layer     | Technology                          |
| --------- | ----------------------------------- |
| Frontend  | React or Vue inside Electron        |
| Backend   | Python (FastAPI or Flask)           |
| Database  | PostgreSQL (local + optional cloud) |
| Kubios    | GUI automation + fallback           |
| AI Assist | Gemini / modular for others         |
| Packaging | Docker / PyInstaller                |
| Testing   | pytest + Cypress/E2E                |

---

## 4. API Specification (Summary)

### Authentication
Users login locally or optionally sync profiles. Hybrid user state.

### Core Endpoints

```
POST   /api/session/upload
GET    /api/session/{id}/status
POST   /api/sync/correct
GET    /api/sync/quality
POST   /api/feature/extract
POST   /api/quality/compute
POST   /api/stress/score
POST   /api/ai/assist
GET    /api/report/{session_id}
```

### AI Assist Endpoint

```
POST /api/ai/assist
Body: {
    user_id,
    session_id (opt),
    prompt_text,
    image_data (opt, base64),
    context_tags
}
```

---

## 5. Database Schema (Key Tables)

### subjects

```sql
CREATE TABLE subjects (
    subject_id UUID PRIMARY KEY,
    name TEXT,
    dob DATE,
    created_at TIMESTAMP
);
```

### sessions

```sql
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
    subject_id UUID REFERENCES subjects(subject_id),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    device_info JSONB,
    created_at TIMESTAMP
);
```

### sync_models

```sql
CREATE TABLE sync_models (
    sync_id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id),
    drift_model JSONB,
    residuals JSONB,
    created_at TIMESTAMP
);
```

### hrv_results

```sql
CREATE TABLE hrv_results (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id),
    measure TEXT,
    value REAL,
    unit TEXT,
    created_at TIMESTAMP
);
```

### eda_features

```sql
CREATE TABLE eda_features (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id),
    tonic_level REAL,
    phasic_count INTEGER,
    created_at TIMESTAMP
);
```

### stress_scores

```sql
CREATE TABLE stress_scores (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id),
    score REAL,
    components JSONB,
    created_at TIMESTAMP
);
```

### quality_scores

```sql
CREATE TABLE quality_scores (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id),
    total_score INTEGER,
    detail JSONB,
    created_at TIMESTAMP
);
```

### user_profiles

```sql
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY,
    username TEXT UNIQUE,
    hashed_password TEXT,
    preferences JSONB,
    created_at TIMESTAMP
);
```

### lab_profile

```sql
CREATE TABLE lab_profile (
    lab_id UUID PRIMARY KEY,
    calibration_settings JSONB,
    preferred_audio_marker JSONB,
    drift_model JSONB,
    updated_at TIMESTAMP
);
```

---

## 6. Kubios Integration Module

### Primary Path — GUI Automation

Backend invokes Kubios via automation tools (AutoIt / AppleScript). It:
1. Prepares RR files and event marker import.
2. Launches Kubios.
3. Applies a saved template.
4. Exports HRV metrics.
5. Backend parses results.

### Fallback Path — Manual Assist

Backend prepares templates. UI guides user to load files and export. Backend ingests results.

---

## 7. Synchronization & Drift Correction

We use a linear time warp model:

```
t_B = a * t_A + b
```

- Fit using matched event markers.
- Compute residuals (RMSE / MAE) to assess alignment quality.
- Auto-heal via cross-correlation or alternative anchors if markers are missing.

---

## 8. Wizard UI Flows

### Lab Setup Wizard
Steps:
1. Detect devices.
2. Run clock sync calibration.
3. Test audio markers.
4. Save lab profile.

### Subject Setup Wizard
1. Enter participant info.
2. EmotiBit placement check.
3. Polar fit check.
4. Pre-stage checklist.
5. Preview markers.

### Analysis Wizard
1. Synchronize streams.
2. Clean artifacts.
3. Extract features.
4. Compute stress score.
5. Explain results.

---

## 9. AI Assistant (Text + Image)

### Capabilities
- Explain concepts.
- Diagnose issues from logs/images.
- Provide setup feedback (e.g., placement).
- Suggest fixes.

### Provider Integration
- Initial: **Gemini**
- Modular: switch to OpenAI / Claude

### Prompt Template Example

```
System: You are an expert lab assistant...
User: {text}
Image: {image}
Context: {wizard step}
```

---

## 10. Quality Scoring

Quality score components:
- Signal integrity.
- Motion artifact fraction.
- Synchronization confidence.
- Event marker coverage.

Example scoring:

```
total_score = w1 * sig + w2 * sync + w3 * artifact + w4 * markers
```

Detailed breakdown stored in JSONB.

---

## 11. Testing & Simulation

- Unit tests for parsers/validators.
- Integration tests with synthetic datasets.
- Simulation of drift, noise, missing events.

Mock datasets stored in tests/simulated/

---

## 12. Deployment & Packaging

### Local Desktop
- Electron + Python backend.
- PostgreSQL local instance.
- Optional cloud sync.

### Cloud-Enabled
- DB hosted.
- Account sync.
- Multi-device access.

---

## 13. Security & Privacy

- Local encryption defaults.
- Cloud sync optional & encrypted.
- Role access, audit logs.

---

## 14. Design Principles

- Self-healing workflows.
- Progressive help.
- AI context-aware assistance.
- Clear separation: lab vs session profiles.
- Tier 3 visuals & accessible explanation.

---

## 15. Next Steps

1. Populate code skeletons.  
2. Build database migrations.  
3. Implement parsers & synchronization logic.  
4. Build wizard UI.  
5. Implement AI assist API.  
6. Integrate Kubios runner.  
7. Build test automation.
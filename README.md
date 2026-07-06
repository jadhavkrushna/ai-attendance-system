# 🎓 Fluentia: AI-Powered Biometric Attendance System

Fluentia is a state-of-the-art, secure, and fully responsive web application that automates classroom attendance using multi-modal biometrics: **Facial Recognition** and **Voiceprint Verification**.

<p align="center">
  <img src="static/img/3d/logo.png" alt="Fluentia Logo" width="120" style="border-radius: 24px; box-shadow: 0 10px 30px rgba(91, 91, 214, 0.2);" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11-blue.svg?style=for-the-badge&logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask" alt="Flask" />
  <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase" alt="Supabase" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker" alt="Docker" />
  <img src="https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render" alt="Render" />
</p>

---

## 🌟 Key Features

* **Dual-Modal Biometrics**: Authenticate students using state-of-the-art face recognition (`dlib` + SVM) and voice verification (`Resemblyzer` + PyTorch).
* **Live Classroom Scanning**: Teachers can capture a camera photo of the entire classroom, automatically recognize all registered students, and log attendance in one click.
* **Premium Dashboard & Analytics**: Beautiful responsive dashboards showing attendance rates, warning indicators (students below 75%), and historical charts.
* **Database Backend**: Secure cloud integration with Supabase for data rosters, subject enrollments, and real-time logs.
* **Fully Responsive Web UI**: Fits beautifully on desktop, tablet, and mobile browsers with a dedicated mobile bottom navigation layout.
* **Interactive REST API**: Pre-integrated dark-mode Swagger UI documentation.

---

## 📐 System Architecture

This diagram shows how student biometrics are captured, verified through our machine learning pipelines, and saved to the cloud database:

```mermaid
graph TD
    User([Student / Teacher]) -->|Interacts with| WebUI[HTML5 Responsive Web UI]
    WebUI -->|Capture Webcam Photo / Voice Clip| Flask[Flask Web Server]
    
    subgraph pipelines ["AI Recognition Pipelines"]
        Flask -->|Extract Landmarks & Encodes| Dlib[dlib / face_recognition]
        Dlib -->|SVM Classification| SVM[Scikit-Learn Classifier]
        
        Flask -->|Audio Processing| Librosa[librosa / webrtcvad]
        Librosa -->|Deep Voice Vectorization| Resemblyzer[Resemblyzer / PyTorch]
    end
    
    subgraph datalayer ["Data Layer"]
        SVM -->|Match Biometrics| Supabase[(Supabase Cloud Database)]
        Resemblyzer -->|Verify Identity| Supabase
    end
    
    Supabase -->|Sync Rosters & Logs| WebUI

    style User fill:#FFD2E5,stroke:#FF4B91,stroke-width:2px,color:#000;
    style WebUI fill:#EBEBFF,stroke:#7C6CF6,stroke-width:2px,color:#000;
    style Flask fill:#E1F5FE,stroke:#0288D1,stroke-width:2px,color:#000;
    style Dlib fill:#E8F5E9,stroke:#4CAF50,stroke-width:2px,color:#000;
    style SVM fill:#FFF9C4,stroke:#FBC02D,stroke-width:2px,color:#000;
    style Librosa fill:#FFE0B2,stroke:#F57C00,stroke-width:2px,color:#000;
    style Resemblyzer fill:#F3E5F5,stroke:#8E24AA,stroke-width:2px,color:#000;
    style Supabase fill:#E0F2F1,stroke:#00796B,stroke-width:2px,color:#000;
    
    style pipelines fill:#F4F6FF,stroke:#7C6CF6,stroke-width:1px,stroke-dasharray: 5 5;
    style datalayer fill:#F0FDFA,stroke:#0D9488,stroke-width:1px,stroke-dasharray: 5 5;
```

---

## 🛠️ Built With

### Web & Backend
* ![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white) **Flask** - Core web server and routing engine.
* ![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=flat-square&logo=gunicorn&logoColor=white) **Gunicorn** - High-performance production WSGI server.
* ![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white) **Supabase** - PostgreSQL cloud database and API middleware.
* ![Swagger](https://img.shields.io/badge/Swagger-85EA2D?style=flat-square&logo=swagger&logoColor=black) **Swagger UI** - Interactive REST API tester.

### Biometrics & AI
* ![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white) **PyTorch** - Neural network engine backing voice embeddings.
* ![Scikit-Learn](https://img.shields.io/badge/scikit_learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white) **Scikit-Learn** - Support Vector Machine (SVM) classification for face profiles.
* ![dlib](https://img.shields.io/badge/dlib-00599C?style=flat-square&logo=c%2B%2B&logoColor=white) **dlib & face-recognition** - Deep learning facial landmark detector.
* ![Librosa](https://img.shields.io/badge/Librosa-FF5500?style=flat-square) **Librosa & webrtcvad** - Audio loading, voice activity detection, and speech feature processing.
* ![Pillow](https://img.shields.io/badge/Pillow-blue?style=flat-square) **Pillow** - Image manipulation pipeline.

---

## 🚀 Quick Start

### Prerequisites
Before running, you need:
- A [Supabase Project](https://supabase.com/) with database tables configured.
- Environment variables configured in a `.env` file in the project root:
  ```env
  SUPABASE_URL=https://your-project.supabase.co
  SUPABASE_KEY=your-supabase-key
  ```

### Option A: Local Run (Direct python)
1. **Initialize Environment**:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
   .\scripts\setup_environment.ps1
   .\.venv\Scripts\Activate.ps1
   ```
2. **Launch Server**:
   ```powershell
   python app.py
   ```
3. Open `http://localhost:5000` in your web browser.

### Option B: Local Run (Docker Compose)
Build and spin up the production container configuration locally:
```bash
docker compose up --build
```
Open `http://localhost:5000` in your browser.

---

## ☁️ Production Deployment

The project is preconfigured to deploy directly to **Render** using Docker:

1. Connect your repository to your **Render Account**.
2. Render will automatically parse [render.yaml](render.yaml) and configure the **Docker Web Service** using the optimized [Dockerfile](Dockerfile).
3. Input the required environment variables (`SUPABASE_URL` and `SUPABASE_KEY`) in the Render configuration dashboard.
4. Render will compile dependencies (compiling `dlib` via single-core to prevent OOM errors) and bring your secure, HTTPS-enabled portal live in 10-15 minutes.

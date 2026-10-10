# ♻️ WasteGuard AI - Real-Time AI Waste Segregation & Compliance Monitoring

WasteGuard AI is a full-stack computer vision application built with **FastAPI** (Python backend) and **React + Vite + TypeScript + Tailwind CSS** (Frontend) for real-time automated waste segregation, anti-contamination monitoring, and compliance auditing.

---

## 🏗️ System Architecture

```
Jasoos Jhamru/
├── backend/
│   ├── main.py                # FastAPI Application & CORS Configuration
│   ├── routes/
│   │   ├── health.py          # GET /api/health & GET /api/model/status
│   │   ├── detect.py          # POST /api/detect/image & POST /api/detect/video
│   │   ├── events.py          # GET /api/events & GET /api/events/export (CSV)
│   │   ├── analytics.py       # GET /api/analytics
│   │   ├── dataset.py         # GET /api/dataset/summary & GET /api/dataset/inspect
│   │   └── config.py          # GET /api/config/segregation
│   └── schemas/
│       └── models.py          # Pydantic Request/Response Models
├── frontend/                  # React + Vite + TypeScript + Tailwind CSS App
│   ├── src/
│   │   ├── components/        # Sidebar, Header, ImageUploader
│   │   ├── pages/             # 9 Interactive Pages (Overview, Scanner, Image, Video, Dataset Lab, Events, Analytics, Health, Settings)
│   │   ├── services/api.ts    # Axios REST API Client
│   │   └── types/             # TypeScript Interfaces
│   ├── package.json
│   └── vite.config.ts
├── configs/
│   └── segregation_rules.yaml # 42-Class Waste Policy (Wet, Dry, Needs Review)
├── src/
│   ├── detector.py            # YOLO / Baseline Demonstration Object Detector
│   ├── segregation.py         # Segregation Rule Engine
│   ├── alerts.py              # Audio Alert Engine & Cooldown Controller
│   ├── event_logger.py        # SQLite Persistence & Analytics
│   ├── video_processor.py     # Video Stream Processor & Deduplication
│   └── dataset_manager.py     # Dataset Inspector & IoU/Precision Evaluator
├── YOLO Waste Detection.v1-v1.yolov8/ # Verified 13,104 image dataset
├── tests/                     # 17 Automated Unit Tests (100% Passing)
├── models/                    # Model Weights
├── snapshots/                 # Violation Image Snapshots
└── logs/                      # SQLite Database (wasteguard_events.db)
```

---

## 🚀 Windows Quick Start Commands

### 1. Start the FastAPI Backend Server
Open a terminal in the project root (`Documents/Jasoos Jhamru`) and run:
```powershell
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive API Docs: **http://127.0.0.1:8000/docs**
- Health Check: **http://127.0.0.1:8000/api/health**

### 2. Start the React Frontend Application
Open a second terminal, navigate to the `frontend/` folder, and run:
```powershell
cd frontend
npm.cmd run dev
```
- Open in your browser: **http://localhost:5173**

---

## 🧪 Testing the Image Upload & Inference Workflow

1. Open **http://localhost:5173** in your web browser.
2. Select **Image Analysis** from the left navigation sidebar.
3. Drag & drop or browse any waste image from your computer (or select a sample from `YOLO Waste Detection.v1-v1.yolov8/test/images/`).
4. Select your target disposal bin: **💧 Wet Waste** or **📦 Dry Waste**.
5. Adjust the confidence threshold (e.g., 35%).
6. Click **Run Waste AI Detection**.
7. The application will display:
   - Visual bounding box overlays (Green for Correct Disposal, Red for Confirmed Violation, Amber for Needs Review).
   - Detected object class, confidence percentage, and compliance explanation.
   - Real-time logging of the event into the SQLite audit database.

---

## 🧪 Run Automated Tests

To execute the complete 17-test suite across the backend and core business logic:
```powershell
python -m unittest discover -s tests -p "test_*.py"
```
Output:
```text
Ran 17 tests in 3.489s
OK (100% Passed)
```

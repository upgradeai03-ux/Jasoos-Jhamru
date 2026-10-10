"""
WasteGuard AI - Real-Time AI Waste Segregation & Monitoring Dashboard
Built with Streamlit, YOLOv8, OpenCV, and SQLite.
"""

import os
import sys
import time
import cv2
import pandas as pd
import numpy as np
import streamlit as st

# Local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.detector import WasteDetector
from src.segregation import SegregationEngine
from src.alerts import AlertEngine
from src.event_logger import EventLogger
from src.video_processor import VideoProcessor
from src.dataset_manager import DatasetManager

# Page Configuration
st.set_page_config(
    page_title="WasteGuard AI - Waste Segregation & Monitoring",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Dark Glassmorphism CSS Styling
st.markdown("""
<style>
    /* Dark Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        color: #f8fafc;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Card Containers */
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }

    /* Status Badges */
    .badge-correct {
        background-color: #059669;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-violation {
        background-color: #dc2626;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-review {
        background-color: #d97706;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }

    /* Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #38bdf8 !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #090d16 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State Singletons
@st.cache_resource
def init_services():
    seg_engine = SegregationEngine()
    event_logger = EventLogger()
    alert_engine = AlertEngine(
        cooldown_seconds=seg_engine.settings.get("alert_cooldown_seconds", 5.0)
    )
    dataset_mgr = DatasetManager()
    
    # Initialize Detector with available model
    available_models = WasteDetector.discover_models()
    model_path = available_models[0]["path"] if available_models else "yolov8n.pt"
    detector = WasteDetector(model_path)

    return seg_engine, event_logger, alert_engine, dataset_mgr, detector

seg_engine, event_logger, alert_engine, dataset_mgr, detector = init_services()

if "video_processor" not in st.session_state:
    st.session_state.video_processor = VideoProcessor(
        detector, seg_engine, event_logger, alert_engine
    )

# Sidebar Navigation & Settings
with st.sidebar:
    st.title("♻️ WasteGuard AI")
    st.caption("Real-Time Segregation & Compliance System")
    st.markdown("---")

    mode = st.radio(
        "Select Operating Mode",
        [
            "📊 Overview Dashboard",
            "🎥 Live Camera Mode",
            "🎬 Video Simulation Mode",
            "🔬 Dataset Testing Lab",
            "📜 Event History & Audit",
            "📈 Analytics & Trends",
            "🏥 System & Model Health",
            "⚙️ Config & Settings",
            "📥 Reports & Export"
        ]
    )

    st.markdown("---")
    st.subheader("🎛️ Live Controls")

    selected_bin = st.radio("Operator Disposal Bin Target", ["Wet Waste", "Dry Waste"], index=1)
    conf_threshold = st.slider("Detection Confidence Cutoff", 0.10, 0.95, 0.35, 0.05)
    alert_enabled = st.toggle("Audio Alerts Enabled", value=True)
    alert_engine.enabled = alert_enabled

    st.markdown("---")
    st.caption("WasteGuard AI v1.0 • Live Hackathon Build")


# Header Section
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.header("WasteGuard AI: Waste Segregation & Compliance Monitor")
    st.caption("Computer Vision Powered Disposal Verification & Anti-Contamination System")

with col_head2:
    status_indicator = "🟢 ONLINE" if detector.is_loaded else "🟡 BASELINE DEMO"
    st.markdown(f"**System Status:** `{status_indicator}`")
    st.markdown(f"**Active Model:** `{detector.model_name}`")

st.markdown("---")


# ==========================================
# 1. OVERVIEW DASHBOARD
# ==========================================
if mode == "📊 Overview Dashboard":
    st.subheader("📊 System Overview & Performance Metrics")
    
    summary = event_logger.get_analytics_summary()
    
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Events", f"{summary['total_events']:,}")
    m2.metric("Correct Disposals", f"{summary['correct_events']:,}")
    m3.metric("Confirmed Violations", f"{summary['confirmed_violations']:,}")
    m4.metric("Needs Review", f"{summary['needs_review_events']:,}")
    m5.metric("Violation Rate", f"{summary['violation_rate_pct']}%")

    st.markdown("---")

    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Disposal Rule Compliance Distribution")
        df_events = event_logger.get_events(limit=500)
        if not df_events.empty:
            result_counts = df_events['rule_result'].value_counts()
            st.bar_chart(result_counts)
        else:
            st.info("No runtime events recorded yet. Run Live Camera, Video Simulation, or Dataset Testing to log events.")

    with col_chart2:
        st.subheader("Recent Disposal Event Stream")
        if not df_events.empty:
            st.dataframe(
                df_events[['timestamp', 'source_mode', 'detected_class', 'confidence', 'selected_bin', 'rule_result']],
                use_container_width=True,
                height=300
            )
        else:
            st.write("Event log database is ready.")


# ==========================================
# 2. LIVE CAMERA MODE
# ==========================================
elif mode == "🎥 Live Camera Mode":
    st.subheader("🎥 Live Camera Segregation Scanner")
    st.caption("Capture live webcam frames, apply detection overlay, and trigger alerts for violations.")

    col_cam_ctrl, col_cam_feed = st.columns([1, 2])

    with col_cam_ctrl:
        st.markdown("### Camera Controls")
        cam_index = st.selectbox("Select Camera Device", [0, 1, 2], index=0)
        run_webcam = st.toggle("Start Live Webcam Stream", value=False)
        
        st.info(f"Target Bin: **{selected_bin}**\n\nConfidence: **{conf_threshold:.2f}**")
        
        if not detector.is_loaded:
            st.warning("No custom YOLO model loaded. Base detection model will be initialized.")

    with col_cam_feed:
        frame_placeholder = st.empty()
        alert_placeholder = st.empty()

        if run_webcam:
            cap = cv2.VideoCapture(cam_index)
            if not cap.isOpened():
                st.error(f"Failed to access webcam at index {cam_index}. Please verify camera availability or switch index.")
            else:
                while run_webcam:
                    ret, frame = cap.read()
                    if not ret:
                        st.error("Error reading frame from webcam.")
                        break

                    # Detect & Evaluate
                    detections = detector.detect(frame, conf_threshold=conf_threshold)
                    evaluations = []
                    for det in detections:
                        eval_res = seg_engine.evaluate_detection(
                            det["class_name"], det["confidence"], selected_bin, conf_threshold
                        )
                        evaluations.append(eval_res)

                        if eval_res["is_violation"]:
                            alert_res = alert_engine.trigger_violation_alert(det["class_name"], selected_bin)
                            if alert_res["visual_warning"]:
                                alert_placeholder.error(f"🚨 ALERT VIOLATION: {eval_res['reason']}")

                    annotated = detector.draw_overlays(frame, detections, evaluations)
                    frame_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                    frame_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
                    time.sleep(0.03)

                cap.release()


# ==========================================
# 3. VIDEO SIMULATION MODE
# ==========================================
elif mode == "🎬 Video Simulation Mode":
    st.subheader("🎬 Video Stream Segregation Simulation")
    st.caption("Simulate disposal stream from a video file with frame deduplication.")

    uploaded_video = st.file_uploader("Upload Video File (.mp4, .avi, .mov)", type=["mp4", "avi", "mov"])
    
    col_v1, col_v2 = st.columns([1, 2])
    
    with col_v1:
        st.markdown("### Simulation Controls")
        if uploaded_video:
            # Save uploaded video to temp file
            temp_vid_path = os.path.join("snapshots", "temp_upload.mp4")
            with open(temp_vid_path, "wb") as f:
                f.write(uploaded_video.read())

            if st.button("▶️ Load & Start Simulation"):
                st.session_state.video_processor.load_video(temp_vid_path)

        if st.session_state.video_processor.is_playing:
            col_b1, col_b2 = st.columns(2)
            if col_b1.button("⏸️ Pause"):
                st.session_state.video_processor.pause()
            if col_b2.button("⏹️ Stop"):
                st.session_state.video_processor.stop()

    with col_v2:
        vid_placeholder = st.empty()
        progress_bar = st.progress(0)

        if st.session_state.video_processor.is_playing and not st.session_state.video_processor.is_paused:
            res = st.session_state.video_processor.process_frame(
                selected_bin=selected_bin,
                conf_threshold=conf_threshold,
                enable_alerts=alert_enabled
            )
            if res:
                frame_rgb = cv2.cvtColor(res["annotated_frame"], cv2.COLOR_BGR2RGB)
                vid_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
                progress_bar.progress(int(res["progress_pct"]))


# ==========================================
# 4. DATASET TESTING LAB
# ==========================================
elif mode == "🔬 Dataset Testing Lab":
    st.subheader("🔬 Roboflow Waste Dataset Inspection & Evaluation Lab")
    st.caption("Inspect verified dataset images, test rule engine, and compare predictions with ground truth.")

    if not dataset_mgr.is_valid:
        st.error("Dataset `data.yaml` not found or invalid.")
    else:
        split = st.selectbox("Dataset Split", ["test", "valid", "train"], index=0)
        img_list = dataset_mgr.get_split_images(split)

        if not img_list:
            st.warning(f"No images found in split '{split}'.")
        else:
            selected_img_name = st.selectbox("Select Sample Image", img_list[:100])
            img_path = os.path.join(dataset_mgr.dataset_dir, split, "images", selected_img_name)

            img_bgr = cv2.imread(img_path)
            if img_bgr is not None:
                gt_boxes = dataset_mgr.load_ground_truth(split, selected_img_name, img_bgr.shape)
                preds = detector.detect(img_bgr, conf_threshold=conf_threshold)

                eval_results = []
                for p in preds:
                    eval_res = seg_engine.evaluate_detection(p["class_name"], p["confidence"], selected_bin, conf_threshold)
                    eval_results.append(eval_res)

                # Generate side-by-side overlays
                pred_overlay = detector.draw_overlays(img_bgr, preds, eval_results)
                gt_overlay = dataset_mgr.draw_ground_truth_overlay(img_bgr, gt_boxes)

                col_img1, col_img2 = st.columns(2)
                with col_img1:
                    st.markdown("### 🎯 Model Predictions & Rule Evaluation")
                    st.image(cv2.cvtColor(pred_overlay, cv2.COLOR_BGR2RGB), use_container_width=True)

                with col_img2:
                    st.markdown("### 🏷️ Ground-Truth Annotations")
                    st.image(cv2.cvtColor(gt_overlay, cv2.COLOR_BGR2RGB), use_container_width=True)

                st.markdown("---")
                st.subheader("📊 Quantitative Detection Evaluation")
                metrics = dataset_mgr.evaluate_image_detections(preds, gt_boxes)
                
                q1, q2, q3, q4 = st.columns(4)
                q1.metric("True Positives (TP)", metrics.get("tp", 0))
                q2.metric("False Positives (FP)", metrics.get("fp", 0))
                q3.metric("Precision", f"{metrics.get('precision', 0.0)*100:.1f}%")
                q4.metric("Recall", f"{metrics.get('recall', 0.0)*100:.1f}%")


# ==========================================
# 5. EVENT HISTORY & AUDIT
# ==========================================
elif mode == "📜 Event History & Audit":
    st.subheader("📜 Persistent Event History Log")
    st.caption("Filtered record of all waste disposal events stored in SQLite.")

    col_f1, col_f2 = st.columns(2)
    filter_mode = col_f1.selectbox("Filter Source Mode", ["All", "Live Camera", "Video Simulation", "Dataset Testing"])
    filter_result = col_f2.selectbox("Filter Rule Result", ["All", "Correct Disposal", "Confirmed Violation", "Needs Review"])

    mode_arg = None if filter_mode == "All" else filter_mode
    res_arg = None if filter_result == "All" else filter_result

    df_events = event_logger.get_events(limit=1000, source_mode=mode_arg, rule_result=res_arg)
    
    if df_events.empty:
        st.info("No matching event records found.")
    else:
        st.dataframe(df_events, use_container_width=True)


# ==========================================
# 6. ANALYTICS & TRENDS
# ==========================================
elif mode == "📈 Analytics & Trends":
    st.subheader("📈 Statistical Analytics & Violation Trends")
    df_all = event_logger.get_events(limit=5000)

    if df_all.empty:
        st.info("No data available yet for analytics. Run live detections to populate metrics.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Class-wise Detection Frequency")
            st.bar_chart(df_all["detected_class"].value_counts())

        with c2:
            st.markdown("### Rule Result Distribution")
            st.bar_chart(df_all["rule_result"].value_counts())


# ==========================================
# 7. SYSTEM & MODEL HEALTH
# ==========================================
elif mode == "🏥 System & Model Health":
    st.subheader("🏥 System Status & Health Diagnostics")
    
    h1, h2 = st.columns(2)
    with h1:
        st.markdown("### 🤖 Detection Model Status")
        st.json({
            "model_path": detector.model_path or "None",
            "model_name": detector.model_name,
            "is_loaded": detector.is_loaded,
            "load_error": detector.load_error_msg or "None",
            "num_classes_in_model": len(detector.class_names)
        })

    with h2:
        st.markdown("### 📁 Dataset Integrity")
        st.json({
            "dataset_dir": dataset_mgr.dataset_dir,
            "is_valid": dataset_mgr.is_valid,
            "num_classes_defined": dataset_mgr.nc
        })


# ==========================================
# 8. CONFIG & SETTINGS
# ==========================================
elif mode == "⚙️ Config & Settings":
    st.subheader("⚙️ Segregation Rules & System Configuration")
    st.markdown("Review and edit active rule engine mappings.")

    st.json(seg_engine.categories)


# ==========================================
# 9. REPORTS & EXPORT
# ==========================================
elif mode == "📥 Reports & Export":
    st.subheader("📥 Export Event Records & Audit Reports")
    st.caption("Generate and download CSV reports of all logged disposal events.")

    df_export = event_logger.get_events(limit=100000)
    csv_data = df_export.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download Full Event Report (CSV)",
        data=csv_data,
        file_name="wasteguard_event_report.csv",
        mime="text/csv"
    )

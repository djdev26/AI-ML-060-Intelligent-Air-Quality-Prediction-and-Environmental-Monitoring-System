"""
Automated Demo Video Recorder for AI-ML-060 Prototype
Records a full interactive demonstration of the web application in HD,
covering dashboard, single prediction, batch prediction, results gallery,
and methodology documentation.
Outputs: AI_ML_060_Prototype_Demo.mp4
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
import imageio_ffmpeg

PROJECT_ROOT = Path(__file__).resolve().parent
TEMP_VIDEO_DIR = PROJECT_ROOT / "temp_video"
TEMP_VIDEO_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_MP4 = PROJECT_ROOT / "AI_ML_060_Prototype_Demo.mp4"
BASE_URL = "http://127.0.0.1:5000"


def smooth_scroll(page, scroll_step=150, delay=0.15, max_scroll=None):
    """Smoothly scroll down the page to simulate realistic user navigation."""
    if max_scroll is None:
        max_scroll = page.evaluate("document.body.scrollHeight")
    current = 0
    while current < max_scroll:
        current += scroll_step
        page.evaluate(f"window.scrollTo(0, {current})")
        time.sleep(delay)
    time.sleep(0.5)


def record_walkthrough():
    print("Launching Chromium for HD Prototype Demonstration Recording...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(TEMP_VIDEO_DIR),
            record_video_size={"width": 1280, "height": 720}
        )
        page = context.new_page()

        # =======================================================
        # SCENE 1: Home Dashboard Walkthrough
        # =======================================================
        print("Scene 1: Home Dashboard Walkthrough...")
        page.goto(f"{BASE_URL}/", wait_until="networkidle")
        time.sleep(3.0)  # Let viewer absorb title and badges
        
        # Highlight Metric Cards
        page.hover(".metric-card, .border-start-teal")
        time.sleep(1.5)
        
        # Smooth scroll down to Model Info and Dataset Characteristics
        smooth_scroll(page, scroll_step=120, delay=0.15, max_scroll=600)
        time.sleep(2.5)
        
        # Smooth scroll down to Key Visualizations (ROC Curves & Feature Importance)
        smooth_scroll(page, scroll_step=120, delay=0.15, max_scroll=1100)
        time.sleep(3.0)
        
        # Scroll back up to navigation bar
        page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
        time.sleep(1.5)

        # =======================================================
        # SCENE 2: Single-Sample Inference (Typical Air Sample)
        # =======================================================
        print("Scene 2: Single-Sample Prediction (Normal / Low CO)...")
        page.click("a[href='/predict']")
        page.wait_for_load_state("networkidle")
        time.sleep(2.0)
        
        # Smooth scroll through sensor input fields
        smooth_scroll(page, scroll_step=150, delay=0.15, max_scroll=500)
        time.sleep(1.0)
        
        # Scroll back to top buttons
        page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
        time.sleep(1.0)
        
        # Click Autofill Typical Air Sample
        print("Clicking Autofill Typical Sample...")
        page.click("#fill-sample-btn")
        time.sleep(1.5)
        
        # Scroll to submit button and click
        page.evaluate("window.scrollTo({top: 800, behavior: 'smooth'})")
        time.sleep(1.0)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        time.sleep(1.0)
        
        # View prediction result (Normal / Low CO result card)
        page.evaluate("window.scrollTo({top: 150, behavior: 'smooth'})")
        time.sleep(3.5)

        # =======================================================
        # SCENE 3: Single-Sample Inference (High CO Pollution Alert)
        # =======================================================
        print("Scene 3: Single-Sample Prediction (High CO Pollution Alert)...")
        page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
        time.sleep(1.0)
        
        # Click Autofill High Pollution Sample
        print("Clicking Autofill High-Pollution Sample...")
        page.click("#fill-high-co-btn")
        time.sleep(1.5)
        
        # Scroll to submit button and click
        page.evaluate("window.scrollTo({top: 800, behavior: 'smooth'})")
        time.sleep(1.0)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        time.sleep(1.0)
        
        # View prediction result (Red High CO Alert card & probability)
        page.evaluate("window.scrollTo({top: 150, behavior: 'smooth'})")
        time.sleep(4.0)

        # =======================================================
        # SCENE 4: Batch CSV Prediction Walkthrough
        # =======================================================
        print("Scene 4: Batch CSV Prediction...")
        page.click("a[href='/batch']")
        page.wait_for_load_state("networkidle")
        time.sleep(2.0)
        
        # Show file upload container
        time.sleep(1.5)
        
        # Select test batch CSV
        sample_csv = PROJECT_ROOT / "data" / "sample_batch_test.csv"
        page.set_input_files("#batchFile", str(sample_csv))
        time.sleep(1.5)
        
        # Click Start Batch Prediction
        page.click("#batch-submit-btn")
        page.wait_for_load_state("networkidle")
        time.sleep(2.0)
        
        # Showcase Batch Results Summary Cards
        smooth_scroll(page, scroll_step=120, delay=0.15, max_scroll=600)
        time.sleep(4.0)  # Pause to inspect preview table with predicted risk badges

        # =======================================================
        # SCENE 5: Analytical Results & Evaluation Gallery
        # =======================================================
        print("Scene 5: Analytical Results & Reports Gallery...")
        page.click("a[href='/results']")
        page.wait_for_load_state("networkidle")
        time.sleep(2.5)
        
        # Inspect Model Performance Comparison Table
        time.sleep(2.0)
        
        # Open Download Reports Dropdown
        page.click(".dropdown-toggle")
        time.sleep(2.0)
        page.click(".dropdown-toggle")  # Close dropdown
        time.sleep(1.0)
        
        # Scroll down through Evaluation Visualizations
        smooth_scroll(page, scroll_step=150, delay=0.15, max_scroll=1200)
        time.sleep(3.0)
        
        # Switch to EDA Tab
        page.evaluate("window.scrollTo({top: 400, behavior: 'smooth'})")
        time.sleep(1.0)
        page.click("#pills-eda-tab")
        time.sleep(2.0)
        
        # Scroll through EDA Visualizations
        smooth_scroll(page, scroll_step=150, delay=0.15, max_scroll=1200)
        time.sleep(3.0)

        # =======================================================
        # SCENE 6: Scientific Methodology & Architecture
        # =======================================================
        print("Scene 6: Methodology & Architecture Documentation...")
        page.click("a[href='/about']")
        page.wait_for_load_state("networkidle")
        time.sleep(2.5)
        
        # Scroll through mathematical formulation and architecture
        smooth_scroll(page, scroll_step=150, delay=0.15, max_scroll=800)
        time.sleep(3.0)
        
        # Finish recording
        print("Finishing demonstration recording...")
        time.sleep(2.0)
        
        context.close()
        browser.close()

    # Locate recorded video
    recorded_videos = list(TEMP_VIDEO_DIR.glob("*.webm"))
    if not recorded_videos:
        raise FileNotFoundError("No recorded video found in temp directory.")
        
    raw_video = recorded_videos[0]
    print(f"Raw Playwright video recorded: {raw_video} ({raw_video.stat().st_size / 1024:.1f} KB)")
    
    # Transcode to high-quality MP4 using FFmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"Transcoding video to MP4 via FFmpeg ({ffmpeg_exe})...")
    
    cmd = [
        ffmpeg_exe,
        "-y",
        "-i", str(raw_video),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        str(OUTPUT_MP4)
    ]
    
    subprocess.run(cmd, check=True)
    print(f"SUCCESS: High-Definition Prototype Demo Video saved to:\n  {OUTPUT_MP4}")
    print(f"Final MP4 Size: {OUTPUT_MP4.stat().st_size / (1024 * 1024):.2f} MB")
    
    # Copy to docs/ for permanent reference
    docs_mp4 = PROJECT_ROOT / "docs" / "AI_ML_060_Prototype_Demo.mp4"
    import shutil
    shutil.copyfile(OUTPUT_MP4, docs_mp4)
    print(f"Copied to: {docs_mp4}")
    
    # Cleanup temp directory
    shutil.rmtree(TEMP_VIDEO_DIR, ignore_errors=True)


if __name__ == "__main__":
    record_walkthrough()

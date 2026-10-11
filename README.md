# Media Variant & Metadata Studio

A local-first Windows desktop studio designed for creators and media managers to generate multiple legitimate export variants and edit technical/descriptive metadata across videos and images.

---

## 🌟 Key Features

### 1. Media Import & Queue
- **Multi-File Import:** Drag-and-drop or browse multiple video (`.mp4`, `.mov`, `.mkv`, `.webm`) and image files (`.jpg`, `.png`, `.webp`).
- **Instant Technical Inspection:** Full display of filename, resolution, duration, framerate (FPS), video & audio bitrates, and file sizes.
- **Non-Destructive:** The source files are **never modified**. All exported variants are saved into a dedicated output folder.

### 2. High-Fidelity Video Processing
- **Stream Copy Mode (Lossless):** Zero re-encoding for bit-for-bit identical video/audio clones when only editing metadata or changing containers.
- **Visually Lossless CRF Mode:** Default CRF 17–18 using `x264` / `x265`, ensuring zero visible compression artifacts or blurring.
- **Aspect Ratio Safe Scaling:**
  - Standard Landscape (1080p, 720p, 4K).
  - Vertical Reel / Shorts (1080x1920) with clean **Pillarbox Padding** (safe, no crop) or **Safe Center Crop**.
  - Square 1:1 (1080x1080).
- **Audio Clarity:** Preserves source audio stream or re-encodes to studio-grade AAC (up to 320 kbps).
- **Optional Volume Normalization:** EBU R128 loudness normalization for broadcast/social standards.
- **GOP / Keyframe Tuning:** Configurable keyframe cadence (e.g., 2.0s standard for web/social fast-seeking).

### 3. Image Processing Engine
- Output format selector: JPEG, PNG, WebP.
- JPEG quality slider (1–100, default 92+).
- EXIF control: Preserve original EXIF, remove EXIF, or inject custom tags.
- Color profile (ICC) preservation.
- Lanczos resampling for pristine resizing.

### 4. Non-Content Metadata Editor
- Clear separation between creative content and metadata tags.
- Fields: **Title, Author / Artist, Creator / Studio, Copyright Notice, Software / Encoder, Creation Date, Keywords / Tags, and Comments**.
- One-click "Set to Now" timestamp utility.
- Optional toggle to strip previous metadata before embedding new tags.

### 5. Multi-Variant Engine (1 to 20 Variants)
- Configure between **1 to 20 independent export variants** simultaneously.
- Each variant has its own codec, resolution, framerate, audio profile, and custom tags.
- One-click presets:
  - *YouTube High-Quality (1080p 60fps)*
  - *Social Reel / Shorts (1080x1920 30fps)*
  - *Square Social Feed (1080x1080 30fps)*
  - *Compact HEVC / H.265 (High Efficiency)*
  - *Lossless Stream Copy (Metadata Only, 0 Re-encode)*
- "Apply to All Variants" button to duplicate settings across cards in 1 click.

### 6. Technical Integrity & Verification (SHA-256)
- Transparent file verification showing:
  - Input SHA-256 vs. Output SHA-256.
  - File size delta (KB/MB).
  - Exact stream count and codecs.
- Strictly legitimate media management: no detection bypass tricks or evasions.

### 7. Modern Dark Desktop UI
- Built with PySide6 (Qt 6) featuring an ultra-sleek dark palette.
- Interactive drag-and-drop zone.
- Real-time progress bars and speed reporting (`speed=3.2x`).
- Cooperative cancellation that terminates background jobs and cleans partial files.
- Live log console with one-click "Open Output Folder" and "Reveal in Explorer".

---

## 🚀 How to Install and Run

### Option 1: Double-Click Standalone Executable (PC Desktop App)
Navigate to the `dist\MediaVariantStudio` folder and double-click:
```plaintext
MediaVariantStudio.exe
```
This executable is self-contained and launches immediately.

---

### Option 2: Use From Your Phone via Wi-Fi Hub 📱
Want to select videos and export variants from your Android phone or iPhone?
1. Double-click `run_mobile_hub.bat` on your PC.
2. The terminal will display your local network link (e.g. `http://192.168.1.6:8080`).
3. Connect your phone to your home Wi-Fi and open that link in your phone browser (Chrome / Safari).
4. Upload videos directly from your phone gallery, tap your social presets, and download the finished variants straight to your phone!

---

### Option 3: 1-Click Windows Launcher (`run.bat`)
Double-click `run.bat` in the project root folder.
The script will automatically verify Python, FFmpeg, and dependencies before starting the studio.

---

### Option 3: Manual Python Startup
1. **Install Python dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
2. **Setup FFmpeg (Automatic):**
   ```powershell
   python setup_ffmpeg.py
   ```
3. **Launch the studio:**
   ```powershell
   python main.py
   ```

---

## 📁 Project Structure

```plaintext
MediaVariantStudio/
│
├── bin/                              # Local FFmpeg & FFprobe binaries
│   ├── ffmpeg.exe
│   └── ffprobe.exe
│
├── core/                             # Core media engine
│   ├── ffmpeg_manager.py             # FFmpeg locator & auto-downloader
│   ├── probe.py                      # FFprobe media analyzer & SHA-256 calculator
│   ├── video_processor.py            # FFmpeg command builder & progress worker
│   ├── image_processor.py            # Pillow engine with Lanczos & ICC preservation
│   ├── metadata_manager.py           # Metadata injection and EXIF handler
│   ├── variant_models.py             # 1-to-20 variant data models & presets
│   └── batch_queue.py                # Threaded queue runner with cancel support
│
├── ui/                               # PySide6 desktop GUI
│   ├── styles/dark_theme.py          # Modern dark QSS stylesheet
│   ├── components/
│   │   ├── drop_area.py              # Drag & drop upload target
│   │   ├── media_table.py            # Queue table with item properties
│   │   ├── tech_info_panel.py        # SHA-256 & stream inspector
│   │   ├── metadata_panel.py         # Metadata form editor
│   │   ├── variant_card.py           # Independent variant configurators
│   │   └── history_panel.py          # Batch queue table & live log console
│   └── main_window.py                # Main application window
│
├── tests/
│   └── test_engine.py                # Baseline verification test suite
│
├── dist/MediaVariantStudio/          # Standalone Windows executable bundle
│   └── MediaVariantStudio.exe
│
├── run.bat                           # 1-click Windows batch launcher
├── requirements.txt                  # Python dependencies
└── README.md                         # This documentation
```

---

## 🔒 Quality & Integrity Guarantee
- **No artificial degradation:** The studio never adds random noise, distortions, or fake artifacts.
- **No copyright evasion:** Strictly designed for content that you own or have permission to publish.
- **Original preservation:** Source files are never modified in place.

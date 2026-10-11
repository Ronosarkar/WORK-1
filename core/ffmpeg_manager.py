import os
import sys
import shutil
import subprocess
import urllib.request
import zipfile
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Base directory of the project (handles PyInstaller bundle and source execution)
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).resolve().parent
    MEIPASS_DIR = Path(getattr(sys, '_MEIPASS', BASE_DIR))
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    MEIPASS_DIR = BASE_DIR

BIN_DIR = BASE_DIR / "bin"

# Well-known static build URL (Gyan.dev official essentials build)
FFMPEG_ZIP_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

def get_bin_dir() -> Path:
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    return BIN_DIR

def find_executable(name: str) -> str | None:
    """Finds an executable in local bin/ or system PATH."""
    exe_name = f"{name}.exe" if sys.platform == "win32" else name
    
    # 1. Local project bin directory
    local_path = BIN_DIR / exe_name
    if local_path.is_file():
        if sys.platform != "win32" and not os.access(str(local_path), os.X_OK):
            try:
                local_path.chmod(local_path.stat().st_mode | 0o755)
            except Exception:
                pass
        return str(local_path)

    # 2. MEIPASS bin directory (PyInstaller internal data)
    meipass_path = MEIPASS_DIR / "bin" / exe_name
    if meipass_path.is_file() and os.access(str(meipass_path), os.X_OK):
        return str(meipass_path)
    
    # 3. Application root directory (if bundled)
    app_root_path = BASE_DIR / exe_name
    if app_root_path.is_file() and os.access(str(app_root_path), os.X_OK):
        return str(app_root_path)

    # 3. System PATH
    system_path = shutil.which(name)
    # 4. Common Windows Winget / Scoop / Chocolatey paths
    if sys.platform == "win32":
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        candidates = [
            Path(local_app_data) / "Microsoft" / "WinGet" / "Links" / exe_name,
            Path("C:/ffmpeg/bin") / exe_name,
            Path("C:/Program Files/ffmpeg/bin") / exe_name,
            Path(os.environ.get("USERPROFILE", "")) / "scoop" / "shims" / exe_name,
        ]
        for c in candidates:
            if c.is_file() and os.access(str(c), os.X_OK):
                return str(c)

    # 5. Check imageio_ffmpeg fallback if available (bundled portable binary)
    if name == "ffmpeg":
        try:
            import imageio_ffmpeg
            pkg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            if pkg_exe and os.path.isfile(pkg_exe):
                return pkg_exe
        except Exception:
            pass

    return None

def get_ffmpeg_path() -> str | None:
    return find_executable("ffmpeg")

def get_ffprobe_path() -> str | None:
    return find_executable("ffprobe")

def is_ffmpeg_available() -> bool:
    return get_ffmpeg_path() is not None and get_ffprobe_path() is not None

def get_ffmpeg_version() -> str:
    path = get_ffmpeg_path()
    if not path:
        return "Not Found"
    try:
        proc = subprocess.run([path, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        first_line = proc.stdout.splitlines()[0] if proc.stdout else "Available"
        return first_line
    except Exception as e:
        return f"Error: {e}"

def download_ffmpeg_essentials(progress_callback=None) -> bool:
    """
    Downloads and extracts ffmpeg.exe and ffprobe.exe into bin/ directory.
    progress_callback can be a function accepting (percent: int, status_message: str).
    """
    bin_dir = get_bin_dir()
    zip_path = bin_dir / "ffmpeg_temp.zip"
    
    try:
        if progress_callback:
            progress_callback(5, "Connecting to FFmpeg repository...")
            
        logger.info(f"Downloading FFmpeg from {FFMPEG_ZIP_URL}...")
        
        def reporthook(block_num, block_size, total_size):
            if total_size > 0 and progress_callback:
                downloaded = block_num * block_size
                percent = int(min(90, 5 + (downloaded / total_size) * 85))
                mb_down = downloaded / (1024 * 1024)
                mb_tot = total_size / (1024 * 1024)
                progress_callback(percent, f"Downloading FFmpeg ({mb_down:.1f}/{mb_tot:.1f} MB)...")

        urllib.request.urlretrieve(FFMPEG_ZIP_URL, str(zip_path), reporthook=reporthook)
        
        if progress_callback:
            progress_callback(92, "Extracting binaries...")
            
        logger.info("Extracting FFmpeg binaries...")
        with zipfile.ZipFile(str(zip_path), 'r') as z:
            for member in z.namelist():
                filename = os.path.basename(member)
                if filename.lower() in ("ffmpeg.exe", "ffprobe.exe"):
                    source = z.open(member)
                    target_path = bin_dir / filename
                    with open(str(target_path), "wb") as target:
                        shutil.copyfileobj(source, target)
                    logger.info(f"Extracted {filename} to {target_path}")

        if zip_path.exists():
            zip_path.unlink()
            
        if progress_callback:
            progress_callback(100, "FFmpeg setup complete!")
            
        return is_ffmpeg_available()
    except Exception as e:
        logger.error(f"Failed to download FFmpeg: {e}")
        if zip_path.exists():
            try:
                zip_path.unlink()
            except Exception:
                pass
        if progress_callback:
            progress_callback(-1, f"Failed: {e}")
        return False

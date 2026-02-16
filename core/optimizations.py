# optimizations.py - GPU detection, Chromium flags, and Windows tweaks for better performance and compatibility.

# importing required libraries
import os
import sys
import platform
import ctypes
import subprocess
import re

DEBUG_MODE = False  # flip to True for verbose console output

# ----- Environment variables (always apply, silent) -----
os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
os.environ.setdefault("QT_SCALE_FACTOR_ROUNDING_POLICY", "PassThrough")
os.environ.setdefault("QTWEBENGINE_REMOTE_DEBUGGING", "0")

# Suppress Qt warnings in release mode, enable verbose logging in debug mode
os.environ["QT_LOGGING_RULES"] = "qt5ct.debug=false;*.warning=false"

# ----- Chromium flags -----
flags = [
    "--ignore-gpu-blocklist",
    "--enable-gpu-rasterization",
    "--enable-zero-copy",
    "--enable-accelerated-2d-canvas",
    "--disable-background-timer-throttling",
    "--no-pings",
    "--disable-breakpad",
    "--disable-domain-reliability",
    "--enable-smooth-scrolling",
    "--enable-parallel-downloading",
]

# Platform-specific optimizations
if platform.system() == "Linux":
    flags.append("--enable-features=VaapiVideoDecoder")

if platform.system() == "Windows":
    flags.append("--use-angle=d3d11")

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join(flags)

# ----- GPU detection -----

# Detect GPU(s) for informational purposes and potential future optimizations
gpu = "Unknown GPU"
if platform.system() == "Windows":
    try:
        ps_cmd = 'powershell -NoProfile -Command "Get-WmiObject Win32_VideoController | Select-Object -ExpandProperty Name"'
        output = subprocess.check_output(ps_cmd, shell=True, text=True, stderr=subprocess.STDOUT)
        gpus = [line.strip() for line in output.splitlines() if line.strip()]
        gpu = ", ".join(gpus) if gpus else "No GPU detected"
    except Exception as e:
        gpu = f"Unknown GPU (failed: {e})"


# Print GPU and applied optimizations in debug mode for transparency, but keep silent in release mode for a cleaner user experience.
if DEBUG_MODE:
    gpu_lower = gpu.lower()
    if "nvidia" in gpu_lower:
        print("[GPU] NVIDIA detected → ANGLE + GPU raster")
    elif "amd" in gpu_lower or "radeon" in gpu_lower:
        print("[GPU] AMD detected → ANGLE + GPU raster")
    elif "intel" in gpu_lower:
        print("[GPU] Intel detected → ANGLE preferred")
    else:
        print("[GPU] Unknown → defaults")

    print(f"[Optimizations] Flags: {' '.join(flags)}")
    print(f"[GPU] Detected: {gpu}")

# ----- Process priority boost -----
try:
    handle = ctypes.windll.kernel32.OpenProcess(0x0200 | 0x0400, False, os.getpid())
    ctypes.windll.kernel32.SetPriorityClass(handle, 0x00008000)  # ABOVE_NORMAL
    if DEBUG_MODE:
        print("[Optimizations] Priority → Above normal")
except Exception as e:
    if DEBUG_MODE:
        print(f"[Optimizations] Priority skipped: {e}")

# ----- Windows DPI awareness -----
if platform.system() == "Windows":
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)  # CONTEXT_PER_MONITOR_AWARE_V2
        if DEBUG_MODE:
            print("[Optimizations] Per-monitor DPI enabled")
    except:
        if DEBUG_MODE:
            print("[Optimizations] DPI awareness failed")

# ----- Verbose Chromium logs only in debug -----
if DEBUG_MODE:
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --enable-logging --v=1"
    print("[DEBUG] Verbose Chromium logging ON")

# Minimal always-on confirmation
print("[Optimizations] Loaded.")
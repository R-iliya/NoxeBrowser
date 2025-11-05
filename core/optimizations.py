# --- optimizations & visuals ---
print("2 Running Optimizations")
# importing required libraries
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
from functools import partial
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import subprocess
import platform
import winreg
import ctypes
import json
import sys
import os
from PyQt5.QtWebEngineCore import (
    QWebEngineUrlRequestInterceptor,
    QWebEngineUrlSchemeHandler,
    QWebEngineUrlScheme,
)


# --- DebugMode, Turn off unless debugging. --- 
# --- Set to True manually for diagnostics. --- 
DEBUG_MODE = False


# os settings
try:
    os.environ["QT_LOGGING_RULES"] = "*=false"
    os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
    os.environ["QTWEBENGINE_DISABLE_GPU_SANDBOX"] = "1"
    os.environ["QT_OPENGL"] = "desktop"
    os.environ["QSG_RENDER_LOOP"] = "threaded"
    os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "PassThrough"
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "0"  # disables unneeded port listener

    flags = [
        "--enable-gpu-rasterization",
        "--enable-zero-copy",
        "--ignore-gpu-blocklist",
        "--enable-native-gpu-memory-buffers",
        "--enable-accelerated-video-decode",
        "--enable-features=VaapiVideoDecoder,ThreadedCompositing,WebRTCPipeWireCapturer",
        "--use-gl=desktop",
        "--in-process-gpu",
        "--process-per-site-instance",
        "--disk-cache-size=104857600",
        "--enable-smooth-scrolling",
        "--enable-fast-unload",
        "--enable-tile-compression",
        "--enable-partial-raster",
        "--enable-parallel-downloading",
        "--disable-background-timer-throttling --disable-backgrounding-occluded-windows",
        "--enable-quic",
        "--disable-renderer-backgrounding",
        "--disable-background-networking",
        "--disable-ipc-flooding-protection",
        "--enable-tcp-fast-open",
        "--enable-webgl-image-chromium",
        "--enable-gpu-compositing",
        "--enable-oop-rasterization",
        "--enable-accelerated-2d-canvas",
        "--enable-native-gpu-memory-buffers",
        "--enable-vulkan",
        "--enable-webgl2-compute-context",
        "--enable-zero-copy",

        "--media-cache-size=157286400",   # ~150MB media cache
        "--enable-main-frame-before-activation",
        "--no-pings",
        "--disable-notifications",
        "--disable-breakpad",             # disable crash reporting overhead
        "--disable-domain-reliability",
        "--disable-component-update",
        "--disable-features=UseSkiaRenderer,CalculateNativeWinOcclusion",

        "--enable-hardware-overlays",
    ]
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join(flags)
except Exception:
    os.environ["QT_QUICK_BACKEND"] = "software"  # optional fallback for hybrid GPUs (helps stability)

# fmt settings
try:
    fmt = QSurfaceFormat()
    QSurfaceFormat.setDefaultFormat(fmt)
    fmt = QSurfaceFormat()
    fmt.setSamples(8)  # anti-aliasing
    fmt.setSwapInterval(1)  # vsync
    fmt.setDepthBufferSize(24)
except Exception:
    pass

# QCoreApplication settings
try:

    try:
        QCoreApplication.setAttribute(Qt.AA_UseDesktopOpenGL)
    except Exception:
        QApplication.setAttribute(Qt.AA_UseOpenGLES)
    
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    QCoreApplication.setAttribute(Qt.AA_UseSoftwareOpenGL, False)
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QCoreApplication.setAttribute(Qt.WA_TranslucentBackground, True)
    # QApplication.setAttribute(Qt.AA_DontUseNativeMenuBar)
    # QApplication.setAttribute(Qt.AA_DontUseNativeDialogs)
except Exception:
    pass

# dynamic gpu flags
gpu = "Unknown GPU"
if platform.system() == "Windows":
    try:
        # Try WMIC first
        gpu = subprocess.getoutput('wmic path win32_VideoController get name').strip().replace("\n\n", ", ")
        if not gpu or "not recognized" in gpu:
            raise Exception("WMIC failed")
    except Exception:
        try:
            # Fallback to Python WMI
            import wmi
            c = wmi.WMI()
            gpu_list = [g.Name for g in c.Win32_VideoController()]
            gpu = ", ".join(gpu_list)
        except Exception:
            gpu = "Unknown GPU"

if "Intel" in gpu:
    os.environ["QT_OPENGL"] = "angle"
    print("Intel GPU detected → using ANGLE backend for stability")

print(f"[GPU detected] {gpu}")

OPT_RESULT = ""

try:
    # Boost current process priority to 'above normal'
    PROCESS_SET_INFORMATION = 0x0200
    PROCESS_QUERY_INFORMATION = 0x0400
    handle = ctypes.windll.kernel32.OpenProcess(PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION, False, os.getpid())
    ctypes.windll.kernel32.SetPriorityClass(handle, 0x00008000)  # ABOVE_NORMAL_PRIORITY_CLASS
    OPT_RESULT = str("Process priority set → Above normal")
except Exception as e:
    OPT_RESULT = str("Priority optimization skipped:", e)

try:
    os.environ["QT_COLOR_MODE"] = "srgb"
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --enable-color-correct-rendering --force-color-profile=srgb"
except Exception:
    pass

try:
    QCoreApplication.setAttribute(Qt.AA_CompressHighFrequencyEvents, False)
    QCoreApplication.setAttribute(Qt.AA_DontCheckOpenGLContextThreadAffinity)
except Exception:
    pass

if DEBUG_MODE:
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --enable-logging --v=1"
    print("[DEBUG] Chromium logging enabled")

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
        "--enable-hardware-overlays",
        "--enable-gpu-memory-buffer-video-frames",
        "--enable-unsafe-webgpu",
        "--disable-frame-rate-limit",
        "--enable-gpu-rasterization",
        "--enable-zero-copy",
        "--ignore-gpu-blocklist",
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
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
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
        "--media-cache-size=157286400",
        "--enable-main-frame-before-activation",
        "--no-pings",
        "--disable-notifications",
        "--disable-breakpad",
        "--disable-domain-reliability",
        "--disable-component-update",
        "--disable-features=UseSkiaRenderer,CalculateNativeWinOcclusion",
        "--prefetch-startup=1",
        "--enable-prefetch-scripts",
        "--enable-speculative-service-worker-startup",
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
gpu = subprocess.getoutput('wmic path win32_VideoController get name')
if "Intel" in gpu:
    os.environ["QT_OPENGL"] = "angle"
    print("Intel GPU detected → using ANGLE backend for stability")

try:
    # Boost current process priority to 'above normal'
    PROCESS_SET_INFORMATION = 0x0200
    PROCESS_QUERY_INFORMATION = 0x0400
    handle = ctypes.windll.kernel32.OpenProcess(PROCESS_SET_INFORMATION | PROCESS_QUERY_INFORMATION, False, os.getpid())
    ctypes.windll.kernel32.SetPriorityClass(handle, 0x00008000)  # ABOVE_NORMAL_PRIORITY_CLASS
    print("\nProcess priority set → Above normal\n")
except Exception as e:
    print("\nPriority optimization skipped:", e,"\n")

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
